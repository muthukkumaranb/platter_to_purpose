import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.food.models import FoodPost

from ..models import Order

User = get_user_model()


class OrderTestCase(TestCase):
    def setUp(self):
        # Create users
        self.donor = User.objects.create_user(
            username="hotel", password="password", role=User.Role.HOTEL
        )
        self.recipient = User.objects.create_user(
            username="orphanage", password="password", role=User.Role.ORPHANAGE
        )

        # Create food post
        self.food = FoodPost.objects.create(
            donor=self.donor,
            title="Test Food",
            description="Delicious test food",
            quantity=10,
            location="Test Location",
        )

    def test_order_creation(self):
        """Test that an order can be created and links correctly."""
        order = Order.objects.create(recipient=self.recipient, food_post=self.food)
        self.assertEqual(order.recipient, self.recipient)
        self.assertEqual(order.food_post, self.food)
        self.assertEqual(order.status, Order.Status.PENDING)

        # Check if food is marked as claimed
        self.food.refresh_from_db()
        self.assertTrue(self.food.is_claimed)

    def test_orders_can_be_filtered_by_recipient(self):
        order = Order.objects.create(recipient=self.recipient, food_post=self.food)

        self.assertEqual(list(Order.objects.for_recipient(self.recipient)), [order])

    def test_secret_token_generation(self):
        """Test that a UUID secret token is generated automatically."""
        order = Order.objects.create(recipient=self.recipient, food_post=self.food)
        self.assertIsInstance(order.secret_token, uuid.UUID)

    def test_pickup_verification_success(self):
        """Test successful pickup verification logic (simulation)."""
        order = Order.objects.create(recipient=self.recipient, food_post=self.food)
        token = str(order.secret_token)

        # Simulate lookup by token
        found_order = Order.objects.get(secret_token=token)
        self.assertEqual(found_order, order)

        # Simulate marking as completed
        found_order.status = Order.Status.COMPLETED
        found_order.save()

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.COMPLETED)

    def test_pickup_verification_invalid_token(self):
        """Test that invalid tokens do not return an order."""
        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(secret_token=uuid.uuid4())
