from django.core.cache import cache
from django.db.models import Sum

from apps.analytics.utils import CO2_KG_PER_MEAL, get_user_badges
from apps.orders.models import Order


def compute_impact(user) -> dict:
    """
    Computes meal savings and environmental impact for a given user.
    """
    if user.is_hotel():
        completed = Order.objects.filter(
            food_post__donor=user,
            status=Order.Status.COMPLETED,
        )
        total_meals = (
            completed.aggregate(total=Sum("food_post__quantity"))["total"] or 0
        )
        co2_prevented = round(total_meals * CO2_KG_PER_MEAL, 1)
        return {
            "meals_saved": total_meals,
            "co2_prevented": co2_prevented,
        }
    else:
        completed = Order.objects.filter(
            recipient=user,
            status=Order.Status.COMPLETED,
        )
        total_meals = (
            completed.aggregate(total=Sum("food_post__quantity"))["total"] or 0
        )
        return {
            "meals_received": total_meals,
        }


def award_badges(user) -> list:
    """
    Computes and returns the list of earned badges for a user, cached for 1 day.
    """
    cache_key = f"user_badges_{user.id}"
    earned_badges = cache.get(cache_key)
    if earned_badges is None:
        if user.is_hotel():
            completed = Order.objects.filter(
                food_post__donor=user,
                status=Order.Status.COMPLETED,
            )
            total_meals = (
                completed.aggregate(total=Sum("food_post__quantity"))["total"] or 0
            )
        else:
            completed = Order.objects.filter(
                recipient=user,
                status=Order.Status.COMPLETED,
            )
            total_meals = (
                completed.aggregate(total=Sum("food_post__quantity"))["total"] or 0
            )

        badges = get_user_badges(total_meals)
        earned_badges = [b for b in badges if b["earned"]]
        cache.set(cache_key, earned_badges, timeout=86400)  # Cache for 1 day
    return earned_badges
