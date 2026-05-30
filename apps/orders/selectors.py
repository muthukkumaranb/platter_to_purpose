from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.orders.models import Order


def get_orders_for_user(user) -> QuerySet[Order]:
    if user.is_hotel():
        return Order.objects.filter(food_post__donor=user)
    return Order.objects.for_recipient(user)


def get_order_by_token(token: str) -> Order:
    return get_object_or_404(Order, secret_token=token)
