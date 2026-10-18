from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.accounts.models import User
from apps.food.models import FoodPost
from apps.orders.models import Order


class SeedDemoCommandTests(TestCase):
    def test_seed_demo_is_idempotent(self):
        call_command("seed_demo", stdout=StringIO())
        first_counts = (
            User.objects.filter(is_demo=True).count(),
            FoodPost.all_objects.filter(donor__is_demo=True).count(),
            Order.all_objects.filter(recipient__is_demo=True).count(),
        )
        call_command("seed_demo", stdout=StringIO())
        second_counts = (
            User.objects.filter(is_demo=True).count(),
            FoodPost.all_objects.filter(donor__is_demo=True).count(),
            Order.all_objects.filter(recipient__is_demo=True).count(),
        )
        self.assertEqual(first_counts, second_counts)
