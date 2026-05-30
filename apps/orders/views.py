from io import BytesIO

import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.exceptions import AppException
from apps.food.selectors import get_food_by_id
from apps.orders.models import Order
from apps.orders.services import claim_food as claim_food_service
from apps.orders.services import verify_pickup as verify_pickup_service
from apps.orders.services import withdraw_order as withdraw_order_service


@login_required
def claim_food(request, food_id):
    food = get_food_by_id(food_id)
    now = timezone.now()

    if food.is_claimed:
        messages.warning(request, "This food has already been claimed.")
        return redirect("food_list")

    if request.method == "POST":
        try:
            claim_food_service(request.user, food_id)
            messages.success(
                request, f'✅ You\'ve claimed "{food.title}"! Check your dashboard.'
            )
            return redirect("dashboard")
        except AppException as e:
            messages.error(request, e.detail)
            return redirect("food_list")
        except Exception:
            messages.error(request, "Something went wrong while claiming this food.")
            return redirect("food_list")

    return render(
        request,
        "orders/claim_confirmation.html",
        {
            "food": food,
            "now_iso": now.isoformat(),
        },
    )


@login_required
def generate_qr(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.user != order.recipient:
        return HttpResponseForbidden("You are not authorized to view this QR code.")

    data = str(order.secret_token)

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")


@login_required
def verify_pickup(request):
    if request.method == "POST":
        token = request.POST.get("token")
        if not token:
            return render(
                request,
                "orders/verify_pickup.html",
                {"error": "Please enter a valid token."},
            )

        try:
            order = verify_pickup_service(token, request.user)
            return render(request, "orders/verify_success.html", {"order": order})
        except AppException as e:
            return render(request, "orders/verify_pickup.html", {"error": e.detail})
        except Exception:
            return render(
                request, "orders/verify_pickup.html", {"error": "Verification failed."}
            )

    return render(request, "orders/verify_pickup.html")


@login_required
def withdraw_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.user != order.recipient:
        return HttpResponseForbidden("You cannot withdraw this order.")

    if request.method == "POST":
        try:
            withdraw_order_service(order_id, request.user)
            messages.success(request, "Order withdrawn successfully.")
            return redirect("dashboard")
        except AppException as e:
            messages.error(request, e.detail)
            return redirect("dashboard")
        except Exception:
            messages.error(request, "Failed to withdraw order.")
            return redirect("dashboard")

    return render(request, "orders/withdraw_confirm.html", {"order": order})
