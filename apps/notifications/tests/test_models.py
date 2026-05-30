from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.food.models import FoodPost
from apps.orders.models import Order

from ..models import Notification

User = get_user_model()


class NotificationSignalTests(TestCase):
    """Tests that signals correctly create notifications."""

    def setUp(self):
        # Create a hotel (donor) and two orphanage users
        self.hotel = User.objects.create_user(
            username="testhotel",
            password="pass123",
            role=User.Role.HOTEL,
            email="hotel@test.com",
        )
        self.orphanage1 = User.objects.create_user(
            username="orphanage1",
            password="pass123",
            role=User.Role.ORPHANAGE,
            email="orph1@test.com",
        )
        self.orphanage2 = User.objects.create_user(
            username="orphanage2",
            password="pass123",
            role=User.Role.ORPHANAGE,
            email="orph2@test.com",
        )

    def test_food_post_creates_notifications_for_orphanages(self):
        """When a hotel posts food, all orphanages should get notified."""
        FoodPost.objects.create(
            donor=self.hotel,
            title="Rice & Curry",
            description="Fresh food",
            quantity=20,
            location="Main St",
            expiry_time=timezone.now() + timedelta(hours=3),
        )
        # Both orphanages should have a notification
        notifs = Notification.objects.filter(
            notification_type=Notification.Type.FOOD_POSTED
        )
        self.assertEqual(notifs.count(), 2)
        self.assertTrue(notifs.filter(user=self.orphanage1).exists())
        self.assertTrue(notifs.filter(user=self.orphanage2).exists())

    def test_order_creates_notification_for_donor(self):
        """When food is claimed, the donor should be notified."""
        food = FoodPost.objects.create(
            donor=self.hotel,
            title="Pasta",
            description="Fresh pasta",
            quantity=10,
            location="2nd Ave",
            expiry_time=timezone.now() + timedelta(hours=2),
        )
        # Clear notifications from food creation
        Notification.objects.all().delete()

        Order.objects.create(recipient=self.orphanage1, food_post=food)
        notifs = Notification.objects.filter(
            notification_type=Notification.Type.FOOD_CLAIMED, user=self.hotel
        )
        self.assertEqual(notifs.count(), 1)
        self.assertIn("Pasta", notifs.first().title)

    def test_pickup_verified_creates_notifications_for_both(self):
        """When pickup is verified, both donor and recipient get notified."""
        food = FoodPost.objects.create(
            donor=self.hotel,
            title="Bread",
            description="Fresh bread",
            quantity=5,
            location="Baker St",
            expiry_time=timezone.now() + timedelta(hours=1),
        )
        order = Order.objects.create(recipient=self.orphanage1, food_post=food)
        # Clear all earlier notifications
        Notification.objects.all().delete()

        # Simulate pickup verification
        order.status = Order.Status.COMPLETED
        order.save()

        pickup_notifs = Notification.objects.filter(
            notification_type=Notification.Type.PICKUP_VERIFIED
        )
        self.assertEqual(pickup_notifs.count(), 2)
        self.assertTrue(pickup_notifs.filter(user=self.hotel).exists())
        self.assertTrue(pickup_notifs.filter(user=self.orphanage1).exists())


class ExpiringFoodCommandTests(TestCase):
    """Tests for the check_expiring_food management command."""

    def setUp(self):
        self.hotel = User.objects.create_user(
            username="expiryhotel",
            password="pass123",
            role=User.Role.HOTEL,
            email="expiry@test.com",
        )

    def test_notifies_for_food_expiring_within_1_hour(self):
        """Food expiring in 30 minutes should trigger a notification."""
        FoodPost.objects.create(
            donor=self.hotel,
            title="Expiring Soup",
            description="Soup",
            quantity=10,
            location="Kitchen",
            expiry_time=timezone.now() + timedelta(minutes=30),
        )
        # Clear any food-post-created notifications
        Notification.objects.all().delete()

        out = StringIO()
        call_command("check_expiring_food", stdout=out)

        notifs = Notification.objects.filter(
            notification_type=Notification.Type.FOOD_EXPIRING, user=self.hotel
        )
        self.assertEqual(notifs.count(), 1)
        self.assertIn("Expiring Soup", notifs.first().title)

    def test_does_not_duplicate_notifications(self):
        """Running the command twice should not create duplicate alerts."""
        FoodPost.objects.create(
            donor=self.hotel,
            title="Expiring Salad",
            description="Salad",
            quantity=5,
            location="Pantry",
            expiry_time=timezone.now() + timedelta(minutes=45),
        )
        Notification.objects.all().delete()

        call_command("check_expiring_food", stdout=StringIO())
        call_command("check_expiring_food", stdout=StringIO())

        notifs = Notification.objects.filter(
            notification_type=Notification.Type.FOOD_EXPIRING
        )
        self.assertEqual(notifs.count(), 1)  # Only one, not two


class NotificationViewTests(TestCase):
    """Tests for the notification views."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="viewuser", password="pass123", role=User.Role.ORPHANAGE
        )
        self.client.login(username="viewuser", password="pass123")
        self.notif = Notification.objects.create(
            user=self.user,
            notification_type=Notification.Type.FOOD_POSTED,
            title="Test Notification",
            message="This is a test.",
        )

    def test_notification_list_page(self):
        """The notification list page should load and show notifications."""
        response = self.client.get("/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Notification")

    def test_mark_as_read(self):
        """Marking a notification as read should update is_read."""
        response = self.client.post(f"/notifications/read/{self.notif.id}/")
        self.assertRedirects(response, "/notifications/")
        self.notif.refresh_from_db()
        self.assertTrue(self.notif.is_read)

    def test_mark_all_read(self):
        """Mark-all-read should update all unread notifications."""
        # Create a second notification
        Notification.objects.create(
            user=self.user,
            notification_type=Notification.Type.FOOD_CLAIMED,
            title="Second Notification",
            message="Another test.",
        )
        response = self.client.post("/notifications/read-all/")
        self.assertRedirects(response, "/notifications/")
        unread = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread, 0)
