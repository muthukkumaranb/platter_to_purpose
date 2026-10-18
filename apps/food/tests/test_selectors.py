from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from apps.food.models import FoodPost
from apps.food.selectors import get_available_food, get_food_by_tab

User = get_user_model()


class FoodSelectorTests(TestCase):
    def setUp(self):
        cache.clear()
        self.donor = User.objects.create_user(
            username="hotel", password="password", role=User.Role.HOTEL
        )

    def test_get_available_food_refreshes_cached_ids_against_current_availability(self):
        available_food = FoodPost.objects.create(
            donor=self.donor,
            title="Available food",
            description="Fresh meals",
            quantity=5,
            location="Downtown",
            priority_window_ends=timezone.now() - timedelta(minutes=1),
        )
        claimed_food = FoodPost.objects.create(
            donor=self.donor,
            title="Claimed food",
            description="Already claimed",
            quantity=3,
            location="Downtown",
            priority_window_ends=timezone.now() - timedelta(minutes=1),
        )

        initial_results = get_available_food(user=None)
        self.assertEqual(initial_results.count(), 2)

        claimed_food.is_claimed = True
        claimed_food.save(update_fields=["is_claimed"])

        refreshed_results = get_available_food(user=None)

        self.assertEqual(refreshed_results.count(), 1)
        self.assertIn(available_food, refreshed_results)
        self.assertNotIn(claimed_food, refreshed_results)

    def test_food_tabs_return_their_own_datasets(self):
        now = timezone.now()
        priority_food = FoodPost.objects.create(
            donor=self.donor,
            title="Priority food",
            description="Reserved meals",
            quantity=5,
            location="Downtown",
            priority_window_ends=now + timedelta(minutes=10),
        )
        claimed_food = FoodPost.objects.create(
            donor=self.donor,
            title="Claimed food",
            description="Already claimed",
            quantity=3,
            location="Downtown",
            is_claimed=True,
            priority_window_ends=now - timedelta(minutes=1),
        )
        expired_food = FoodPost.objects.create(
            donor=self.donor,
            title="Expired food",
            description="Past expiry",
            quantity=2,
            location="Downtown",
            expiry_time=now - timedelta(minutes=1),
            priority_window_ends=now - timedelta(minutes=2),
        )

        self.assertIn(priority_food, get_food_by_tab(self.donor, "priority"))
        self.assertIn(claimed_food, get_food_by_tab(self.donor, "claimed"))
        self.assertIn(expired_food, get_food_by_tab(self.donor, "expired"))
        self.assertNotIn(claimed_food, get_food_by_tab(self.donor, "available"))
