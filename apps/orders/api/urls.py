from django.urls import path

from apps.orders.api.views import ClaimFoodView, VerifyPickupView, WithdrawOrderView

urlpatterns = [
    path("claim/<int:food_id>/", ClaimFoodView.as_view(), name="api_claim_food"),
    path("verify/<str:token>/", VerifyPickupView.as_view(), name="api_verify_pickup"),
    path("<int:pk>/withdraw/", WithdrawOrderView.as_view(), name="api_withdraw_order"),
]
