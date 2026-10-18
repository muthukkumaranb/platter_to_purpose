"""
View tests for the food app.
"""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.food.models import FoodPost


class FoodViewTests(TestCase):
    def test_food_detail_renders_template_values(self):
        donor = User.objects.create_user(
            username="formatting-hotel",
            password="test-password",
            role=User.Role.HOTEL,
        )
        food = FoodPost.objects.create(
            donor=donor,
            title="Formatting Test Meal",
            description="A test donation.",
            quantity=12,
            location="Test Kitchen",
            expiry_time=timezone.now() + timedelta(hours=2),
        )

        response = self.client.get(reverse("food_detail", args=[food.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Formatting Test Meal")
        self.assertNotContains(response, "{{ food.title }}")
        self.assertNotContains(response, '{{ food.expiry_time|date:"g:i A" }}')
