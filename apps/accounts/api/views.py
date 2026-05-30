from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    VerifyOtpSerializer,
)
from apps.accounts.tasks import send_otp_task
from apps.accounts.utils import generate_otp

User = get_user_model()


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False  # Deactivate until OTP verified
            user.save()

            # Generate OTP & store in cache
            otp = generate_otp()
            cache.set(f"otp_{user.username}", otp, timeout=600)  # 10 minutes TTL

            # Send OTP asynchronously via Celery
            if user.phone:
                send_otp_task.delay(user.phone, otp)

            return Response(
                {
                    "message": "User registered successfully. Please verify OTP sent to your phone.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            entered_otp = serializer.validated_data["otp"]

            cached_otp = cache.get(f"otp_{username}")
            if cached_otp and entered_otp == cached_otp:
                user = get_object_or_404(User, username=username)
                user.is_active = True
                user.save()
                cache.delete(f"otp_{username}")  # Clear cache
                return Response(
                    {"message": "Phone verification successful. You can now log in."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": "invalid_otp", "detail": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
