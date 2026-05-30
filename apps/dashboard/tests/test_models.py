from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class DashboardRedesignTestCase(TestCase):
    def setUp(self):
        self.hotel = User.objects.create_user(
            username="hotel", password="password", role=User.Role.HOTEL
        )
        self.orphanage = User.objects.create_user(
            username="orphanage", password="password", role=User.Role.ORPHANAGE
        )

    def test_hotel_dashboard_redesign(self):
        # Create a post
        from apps.food.models import FoodPost

        FoodPost.objects.create(
            donor=self.hotel,
            title="Tasty Donuts",
            description="Fresh donuts",
            quantity=10,
            location="Hotel Lobby",
        )
        self.client.login(username="hotel", password="password")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        # Check for new design elements
        self.assertContains(response, "Total Donations")
        self.assertContains(response, "Meals Impacted")
        self.assertContains(response, "Verify\n                    Pickup")
        self.assertContains(response, "My Active Posts")
        # Check for dynamic data (count should be 1)
        self.assertContains(response, "1")
        self.assertNotContains(response, "{{ my_posts.count }}")

    def test_orphanage_dashboard_redesign(self):
        # Create an order
        from apps.food.models import FoodPost
        from apps.orders.models import Order

        food = FoodPost.objects.create(
            donor=self.hotel,
            title="Tasty Donuts",
            description="Fresh donuts",
            quantity=10,
            location="Hotel Lobby",
        )
        Order.objects.create(recipient=self.orphanage, food_post=food)
        self.client.login(username="orphanage", password="password")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        # Check for new design elements
        self.assertContains(response, "Orders Placed")
        self.assertContains(response, "Find food donations:")
        self.assertContains(response, "My Orders")
        self.assertContains(response, "Pickup Pass")
        # Check for dynamic data (count should be 1)
        self.assertContains(response, "1")
        self.assertNotContains(response, "{{ my_orders.count }}")
