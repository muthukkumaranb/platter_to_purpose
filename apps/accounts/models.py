from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.accounts.constants import UserRole


class User(AbstractUser):
    Role = UserRole

    role = models.CharField(
        max_length=50, choices=UserRole.choices, default=UserRole.HOTEL, db_index=True
    )

    # Add any common fields like phone, address, etc. if needed
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def is_hotel(self):
        return self.role == self.Role.HOTEL

    def is_orphanage(self):
        return self.role == self.Role.ORPHANAGE

    @property
    def average_rating(self):
        from django.db.models import Avg

        from apps.feedback.models import Feedback

        # Feedback -> Order -> FoodPost -> Donor (User)
        result = Feedback.objects.filter(order__food_post__donor=self).aggregate(
            Avg("rating")
        )
        return result["rating__avg"] or 0
