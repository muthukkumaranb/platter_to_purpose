import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import cache_page

from apps.analytics.selectors import get_platform_stats, get_user_stats
from apps.analytics.services import award_badges
from apps.feedback.models import Feedback
from apps.orders.models import Order


@cache_page(60 * 5)  # Cache for 5 minutes
def public_impact(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    # platform stats from selector
    stats = get_platform_stats()

    # Completed orders
    completed = Order.objects.filter(status=Order.Status.COMPLETED)

    # Daily Donations (last 30 days)
    daily_data = (
        completed.filter(claimed_at__gte=thirty_days_ago)
        .extra(select={"day": "DATE(claimed_at)"})
        .values("day")
        .annotate(meals=Sum("food_post__quantity"))
        .order_by("day")
    )

    chart_labels = []
    chart_values = []
    daily_dict = {str(row["day"]): row["meals"] for row in daily_data}

    for i in range(30):
        day = (thirty_days_ago + timedelta(days=i)).date()
        day_str = str(day)
        chart_labels.append(day.strftime("%b %d"))
        chart_values.append(daily_dict.get(day_str, 0))

    # Top 5 Donors
    top_donors = (
        completed.values("food_post__donor__username")
        .annotate(total_meals=Sum("food_post__quantity"))
        .order_by("-total_meals")[:5]
    )
    donor_labels = [d["food_post__donor__username"] for d in top_donors]
    donor_values = [d["total_meals"] for d in top_donors]

    # Top 5 Recipients
    top_recipients = (
        completed.values("recipient__username")
        .annotate(total_meals=Sum("food_post__quantity"))
        .order_by("-total_meals")[:5]
    )

    # Live Feed
    recent = completed.select_related(
        "food_post", "food_post__donor", "recipient"
    ).order_by("-claimed_at")[:10]
    live_feed = []
    for order in recent:
        live_feed.append(
            {
                "location": order.food_post.location,
                "meals": order.food_post.quantity,
                "time": order.claimed_at.isoformat(),
                "time_display": _time_ago(order.claimed_at, now),
            }
        )

    context = {
        "total_meals": stats["total_meals"],
        "active_donors": stats["active_donors"],
        "orphanages_served": stats["orphanages_served"],
        "co2_prevented": stats["co2_prevented"],
        "chart_labels_json": json.dumps(chart_labels),
        "chart_values_json": json.dumps(chart_values),
        "donor_labels_json": json.dumps(donor_labels),
        "donor_values_json": json.dumps(donor_values),
        "top_donors": top_donors,
        "top_recipients": top_recipients,
        "live_feed_json": json.dumps(live_feed),
        "live_feed": live_feed,
    }
    return render(request, "analytics/impact_public.html", context)


def live_feed_api(request):
    now = timezone.now()
    completed = (
        Order.objects.filter(status=Order.Status.COMPLETED)
        .select_related("food_post")
        .order_by("-claimed_at")[:10]
    )
    feed = []
    for order in completed:
        feed.append(
            {
                "location": order.food_post.location,
                "meals": order.food_post.quantity,
                "time_display": _time_ago(order.claimed_at, now),
            }
        )
    return JsonResponse({"feed": feed})


@login_required
def personal_impact(request):
    user = request.user
    now = timezone.now()

    stats = get_user_stats(user)
    badges = award_badges(user)

    context = {
        **stats,
        "user": user,
        "badges": badges,
    }

    if user.is_hotel():
        completed = Order.objects.filter(
            food_post__donor=user,
            status=Order.Status.COMPLETED,
        ).select_related("food_post")
        monthly_labels, monthly_values = _monthly_breakdown(
            completed, "claimed_at", "food_post__quantity", now
        )
        context["monthly_labels_json"] = json.dumps(monthly_labels)
        context["monthly_values_json"] = json.dumps(monthly_values)
        from apps.analytics.utils import get_next_badge

        context["next_badge"] = get_next_badge(stats["total_meals"])
    else:
        completed = Order.objects.filter(
            recipient=user,
            status=Order.Status.COMPLETED,
        ).select_related("food_post", "food_post__donor")
        feedback_left = (
            Feedback.objects.filter(order__recipient=user)
            .select_related("order", "order__food_post", "order__food_post__donor")
            .order_by("-created_at")
        )
        monthly_labels, monthly_values = _monthly_breakdown(
            completed, "claimed_at", "food_post__quantity", now
        )
        context["monthly_labels_json"] = json.dumps(monthly_labels)
        context["monthly_values_json"] = json.dumps(monthly_values)
        context["feedback_left"] = feedback_left

        favorite_donor_data = (
            completed.values("food_post__donor__username")
            .annotate(order_count=Count("id"))
            .order_by("-order_count")
            .first()
        )
        context["favorite_donor"] = (
            favorite_donor_data["food_post__donor__username"]
            if favorite_donor_data
            else "N/A"
        )

    return render(request, "analytics/impact_personal.html", context)


def _monthly_breakdown(queryset, date_field, sum_field, now):
    labels = []
    values = []
    for i in range(11, -1, -1):
        month_date = (now - timedelta(days=i * 30)).replace(day=1)
        month_name = month_date.strftime("%b %Y")
        if month_date.month == 12:
            next_month = month_date.replace(year=month_date.year + 1, month=1)
        else:
            next_month = month_date.replace(month=month_date.month + 1)

        month_total = (
            queryset.filter(
                **{
                    f"{date_field}__gte": month_date,
                    f"{date_field}__lt": next_month,
                }
            ).aggregate(total=Sum(sum_field))["total"]
            or 0
        )

        labels.append(month_name)
        values.append(month_total)
    return labels, values


def _time_ago(dt, now):
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        mins = seconds // 60
        return f"{mins} minute{'s' if mins != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
