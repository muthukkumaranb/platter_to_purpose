from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.accounts.api.views import UserRegistrationView, VerifyOtpView

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="api_register"),
    path("verify-otp/", VerifyOtpView.as_view(), name="api_verify_otp"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
