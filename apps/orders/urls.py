from django.urls import path

from . import views

urlpatterns = [
    path("claim/<int:food_id>/", views.claim_food, name="claim_food"),
    path("qr/<int:order_id>/", views.generate_qr, name="generate_qr"),
    path("verify/", views.verify_pickup, name="verify_pickup"),
    path("withdraw/<int:order_id>/", views.withdraw_order, name="withdraw_order"),
]
