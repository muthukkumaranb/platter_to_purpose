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

    def test_claimed_tab_shows_claimed_food_only(self):
        donor = User.objects.create(
            username="tab-hotel",
            role=User.Role.HOTEL,
        )
        claimed_food = FoodPost.objects.create(
            donor=donor,
            title="Claimed tab meal",
            description="Already claimed.",
            quantity=8,
            location="Test Kitchen",
            is_claimed=True,
        )
        available_food = FoodPost.objects.create(
            donor=donor,
            title="Available tab meal",
            description="Still available.",
            quantity=8,
            location="Test Kitchen",
            priority_window_ends=timezone.now() - timedelta(minutes=1),
        )

        response = self.client.get(
            reverse("food_list"), {"filter": "claimed"}
        )

        self.assertContains(response, claimed_food.title)
        self.assertNotContains(response, available_food.title)
