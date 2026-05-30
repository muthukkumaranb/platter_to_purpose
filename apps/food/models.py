from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import SoftDeleteManager, SoftDeleteMixin, SoftDeleteQuerySet


class FoodPostQuerySet(SoftDeleteQuerySet):
    def available(self):
        now = timezone.now()
        return self.filter(is_claimed=False).filter(
            models.Q(expiry_time__isnull=True) | models.Q(expiry_time__gt=now)
        )

    def by_donor(self, user):
        return self.filter(donor=user)


class FoodPostManager(SoftDeleteManager):
    def get_queryset(self):
        return FoodPostQuerySet(self.model, using=self._db).active()


class FoodPost(SoftDeleteMixin, models.Model):
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="food_posts",
        db_index=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    quantity = models.PositiveIntegerField(help_text="Number of servings/meals")
    location = models.CharField(max_length=255)
    expiry_time = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_claimed = models.BooleanField(default=False, db_index=True)
    image = models.ImageField(upload_to="food_images/", blank=True, null=True)

    priority_window_ends = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the priority claiming window for orphanages expires.",
    )

    objects = FoodPostManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.donor.username}"

    def save(self, *args, **kwargs):
        if not self.pk and self.priority_window_ends is None:
            window_minutes = getattr(settings, "PRIORITY_WINDOW_MINUTES", 30)
            if window_minutes > 0:
                self.priority_window_ends = timezone.now() + timedelta(
                    minutes=window_minutes
                )
        super().save(*args, **kwargs)

    @property
    def is_in_priority_window(self):
        if self.is_claimed or not self.priority_window_ends:
            return False
        return timezone.now() < self.priority_window_ends

    @property
    def priority_status(self):
        if self.is_claimed:
            return "claimed"
        if self.is_in_priority_window:
            return "priority"
        return "open"

    def get_rating_stars(self):
        if hasattr(self, "order") and hasattr(self.order, "feedback"):
            return "⭐" * self.order.feedback.rating
        return ""
