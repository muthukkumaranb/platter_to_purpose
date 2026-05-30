from django.db import models


class NotificationType(models.TextChoices):
    FOOD_POSTED = "FOOD_POSTED", "New Food Available"
    FOOD_CLAIMED = "FOOD_CLAIMED", "Food Claimed"
    PICKUP_VERIFIED = "PICKUP_VERIFIED", "Pickup Verified"
    FOOD_EXPIRING = "FOOD_EXPIRING", "Food Expiring Soon"
    PRIORITY_OPEN = "PRIORITY_OPEN", "Priority Window Open"
    PRIORITY_EXPIRED = "PRIORITY_EXPIRED", "Priority Window Expired"
