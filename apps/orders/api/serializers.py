from rest_framework import serializers

from apps.accounts.api.serializers import UserSerializer
from apps.food.api.serializers import FoodPostSerializer
from apps.orders.models import Order


class OrderSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(read_only=True)
    food_post = FoodPostSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "recipient",
            "food_post",
            "claimed_at",
            "secret_token",
            "status",
        )
        read_only_fields = ("secret_token",)
