from rest_framework import serializers

from apps.accounts.api.serializers import UserSerializer
from apps.food.models import FoodPost


class FoodPostSerializer(serializers.ModelSerializer):
    donor = UserSerializer(read_only=True)
    is_in_priority_window = serializers.ReadOnlyField()
    priority_status = serializers.ReadOnlyField()

    class Meta:
        model = FoodPost
        fields = (
            "id",
            "donor",
            "title",
            "description",
            "quantity",
            "location",
            "expiry_time",
            "created_at",
            "updated_at",
            "is_claimed",
            "image",
            "priority_window_ends",
            "is_in_priority_window",
            "priority_status",
        )
        read_only_fields = ("is_claimed", "priority_window_ends")
