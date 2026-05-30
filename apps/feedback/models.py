from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.orders.models import Order


class Feedback(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="feedback", db_index=True
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Feedback for Order #{self.order.id} - {self.rating} Stars"
