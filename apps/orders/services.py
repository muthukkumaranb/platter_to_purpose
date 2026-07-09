from datetime import timedelta

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.food.exceptions import FoodPostNotFoundException, FoodPostReservedException
from apps.food.models import FoodPost
from apps.orders.constants import OrderStatus
from apps.orders.exceptions import (
    FoodAlreadyClaimedException,
    InvalidPickupTokenException,
    OrderAlreadyCompletedException,
    OrderWithdrawalWindowExpiredException,
    UnauthorizedOrderActionException,
)
from apps.orders.models import Order


def claim_food(user, food_id) -> Order:
    """
    Claim a food post. Uses select_for_update to protect against concurrent claims.
    Invalidates available food cache.
    """
    with transaction.atomic():
        try:
            locked_food = FoodPost.objects.select_for_update().get(pk=food_id)
        except FoodPost.DoesNotExist as exc:
            raise FoodPostNotFoundException() from exc

        if locked_food.is_claimed:
            raise FoodAlreadyClaimedException()

        if locked_food.is_in_priority_window and user.is_hotel():
            raise FoodPostReservedException()

        order = Order.objects.create(
            recipient=user,
            food_post=locked_food,
        )

        # Invalidate available food cache
        cache.delete("available_food_ids")
        return order


def verify_pickup(token, user) -> Order:
    """
    Verify order pickup using the unique token.
    Invalidates platform stats and user badge caches.
    """
    try:
        order = Order.objects.get(secret_token=token)
    except (Order.DoesNotExist, ValueError):
        raise InvalidPickupTokenException()

    # Ensure the logged-in user is the donor of the food post
    if order.food_post.donor != user:
        raise UnauthorizedOrderActionException("This order does not belong to you.")

    if order.status == OrderStatus.COMPLETED:
        raise OrderAlreadyCompletedException()

    order.status = OrderStatus.COMPLETED
    order.save()

    # Invalidate stats and user badges caches
    cache.delete("platform_impact_stats")
    cache.delete(f"user_badges_{order.food_post.donor.id}")
    cache.delete(f"user_badges_{order.recipient.id}")

    return order


def withdraw_order(order_id, user):
    """
    Withdraw/cancel an order within the 5-minute cancellation window.
    Invalidates available food cache.
    """
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        raise Order.DoesNotExist("This order does not exist.")

    if order.recipient != user:
        raise UnauthorizedOrderActionException("You cannot withdraw this order.")

    time_elapsed = timezone.now() - order.claimed_at
    if time_elapsed > timedelta(minutes=5):
        raise OrderWithdrawalWindowExpiredException()

    with transaction.atomic():
        food = order.food_post
        food.is_claimed = False
        food.save()
        order.delete()

        # Invalidate available food cache
        cache.delete("available_food_ids")
