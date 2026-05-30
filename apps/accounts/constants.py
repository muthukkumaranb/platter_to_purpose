from django.db import models


class UserRole(models.TextChoices):
    HOTEL = "HOTEL", "Hotel"
    ORPHANAGE = "ORPHANAGE", "Orphanage"
