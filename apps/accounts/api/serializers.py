from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.constants import UserRole

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "phone", "address")


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "role", "phone", "address")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            role=validated_data.get("role", UserRole.HOTEL),
            phone=validated_data.get("phone", ""),
            address=validated_data.get("address", ""),
        )
        return user


class VerifyOtpSerializer(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField(max_length=6)
