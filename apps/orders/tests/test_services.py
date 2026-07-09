from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.food.models import FoodPost
from apps.orders.exceptions import (
    FoodAlreadyClaimedException,
    OrderWithdrawalWindowExpiredException,
    UnauthorizedOrderActionException,
)
from apps.orders.models import Order
from apps.orders.services import claim_food, withdraw_order

User = get_user_model()


class OrderServiceTests(TestCase):
    def setUp(self):
        self.donor = User.objects.create_user(
            username="hotel", password="password", role=User.Role.HOTEL
        )
        self.recipient = User.objects.create_user(
            username="orphanage", password="password", role=User.Role.ORPHANAGE
        )
        self.food = FoodPost.objects.create(
            donor=self.donor,
            title="Soup",
            description="Hot soup",
            quantity=4,
            location="Central",
        )

    def test_claim_food_prevents_duplicate_claims(self):
        claim_food(self.recipient, self.food.pk)

        with self.assertRaises(FoodAlreadyClaimedException):
            claim_food(self.recipient, self.food.pk)

    def test_withdraw_order_only_allows_the_claiming_user(self):
        order = claim_food(self.recipient, self.food.pk)

        with self.assertRaises(UnauthorizedOrderActionException):
            withdraw_order(order.pk, self.donor)

    def test_withdraw_order_rejects_expired_cancellation_window(self):
        order = claim_food(self.recipient, self.food.pk)
        order.claimed_at = order.claimed_at - timedelta(minutes=6)
        order.save(update_fields=["claimed_at"])

        with self.assertRaises(OrderWithdrawalWindowExpiredException):
            withdraw_order(order.pk, self.recipient)
