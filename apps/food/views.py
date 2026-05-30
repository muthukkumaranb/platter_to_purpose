from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.analytics.selectors import get_user_stats
from apps.food.forms import FoodPostForm
from apps.food.selectors import get_available_food, get_food_by_id
from apps.food.services import post_food_donation


def food_list(request):
    now = timezone.now()

    # Read filter params from URL
    query = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()
    min_qty = request.GET.get("min_qty", "").strip()
    sort = request.GET.get("sort", "newest").strip()

    # Call Selector layer
    foods = get_available_food(
        user=request.user, q=query, location=location, min_qty=min_qty, sort=sort
    )

    total_count = foods.count()
    filtered_count = total_count

    # Dashboard card stats computed using selector
    urgency_threshold = now + timedelta(hours=2)
    all_available = get_available_food(user=request.user)

    priority_count = all_available.filter(
        priority_window_ends__isnull=False,
        priority_window_ends__gt=now,
    ).count()

    expiring_count = all_available.filter(
        expiry_time__lte=urgency_threshold,
    ).count()

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    new_today = all_available.filter(created_at__gte=today_start).count()

    priority_window_food = (
        all_available.filter(
            priority_window_ends__isnull=False,
            priority_window_ends__gt=now,
        )
        .order_by("priority_window_ends")
        .first()
    )
    priority_window_ends = (
        priority_window_food.priority_window_ends if priority_window_food else None
    )

    # User-specific stats for sidebar
    user = request.user
    is_orphanage = user.is_authenticated and user.is_orphanage()
    is_hotel = user.is_authenticated and user.is_hotel()

    user_meals = 0
    user_co2 = "0"
    user_pickups = 0
    recent_pickups = 0

    if user.is_authenticated:
        stats = get_user_stats(user)
        if is_orphanage:
            user_meals = stats.get("total_meals", 0)
            user_co2 = f"{round(user_meals * 2.5 / 1000, 1)}t"

            from apps.orders.selectors import get_orders_for_user

            user_pickups = get_orders_for_user(user).completed().count()
            week_ago = now - timedelta(days=7)
            recent_pickups = (
                get_orders_for_user(user)
                .completed()
                .filter(claimed_at__gte=week_ago)
                .count()
            )


    context = {
        "foods": foods,
        "total_count": total_count,
        "filtered_count": filtered_count,
        "urgency_threshold": urgency_threshold,
        "now_iso": now.isoformat(),
        "is_orphanage": is_orphanage,
        "is_hotel": is_hotel,
        "priority_count": priority_count,
        "expiring_count": expiring_count,
        "new_today": new_today,
        "priority_window_ends": priority_window_ends,
        "user_meals": user_meals,
        "user_co2": user_co2,
        "user_pickups": user_pickups,
        "recent_pickups": recent_pickups,
        "current_query": query,
        "current_location": location,
        "current_min_qty": min_qty,
        "current_sort": sort,
        "sort_newest": sort == "newest",
        "sort_expiry": sort == "expiry",
        "sort_quantity": sort == "quantity",
    }

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "food/food_list_partial_v2.html", context)
    return render(request, "food/food_list_v2.html", context)


def food_detail(request, pk):
    food = get_food_by_id(pk)
    now = timezone.now()
    user = request.user
    is_orphanage = user.is_authenticated and user.is_orphanage()
    is_hotel = user.is_authenticated and user.is_hotel()

    context = {
        "food": food,
        "is_orphanage": is_orphanage,
        "is_hotel": is_hotel,
        "now_iso": now.isoformat(),
    }
    return render(request, "food/food_detail_v2.html", context)


@login_required
def post_food(request):
    if not request.user.role == "HOTEL":
        return redirect("home")

    if request.method == "POST":
        try:
            post_food_donation(request.user, request.POST, request.FILES)
            messages.success(request, "✅ Food donation posted successfully!")
            return redirect("dashboard")
        except ValidationError as e:
            form = FoodPostForm(request.POST, request.FILES)
            if hasattr(e, "message_dict") and e.message_dict:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            elif hasattr(e, "messages"):
                for msg in e.messages:
                    form.add_error(None, msg)
            else:
                form.add_error(None, str(e))
    else:
        form = FoodPostForm()
    return render(request, "food/food_post.html", {"form": form})
