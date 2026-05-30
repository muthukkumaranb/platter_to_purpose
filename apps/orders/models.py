import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import SoftDeleteManager, SoftDeleteMixin, SoftDeleteQuerySet
from apps.food.models import FoodPost
from apps.orders.constants import OrderStatus


class OrderQuerySet(SoftDeleteQuerySet):
    def pending(self):
        return self.filter(status=OrderStatus.PENDING)

    def completed(self):
        return self.filter(status=OrderStatus.COMPLETED)

    def for_recipient(self, user):
        return self.filter(recipient=user)


class OrderManager(SoftDeleteManager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db).active()


class Order(SoftDeleteMixin, models.Model):
    Status = OrderStatus

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        db_index=True,
    )
    food_post = models.OneToOneField(
        FoodPost, on_delete=models.CASCADE, related_name="order", db_index=True
    )
    claimed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    secret_token = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    status = models.CharField(
        max_length=20,
        default=OrderStatus.PENDING,
        choices=OrderStatus.choices,
        db_index=True,
    )

    objects = OrderManager()

    class Meta:
        ordering = ["-claimed_at"]

    def __str__(self):
        return f"Order for {self.food_post.title} by {self.recipient.username}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.food_post.is_claimed = True
            self.food_post.save()
        super().save(*args, **kwargs)
