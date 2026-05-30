from django.core.cache import cache
from django.db.models import Sum

from apps.analytics.utils import CO2_KG_PER_MEAL
from apps.food.models import FoodPost
from apps.orders.models import Order


def get_platform_stats() -> dict:
    """
    Retrieves global metrics, caching them for 5 minutes.
    """
    cache_key = "platform_impact_stats"
    stats = cache.get(cache_key)
    if stats is None:
        completed = Order.objects.filter(status=Order.Status.COMPLETED)
        total_meals = (
            completed.aggregate(total=Sum("food_post__quantity"))["total"] or 0
        )
        active_donors = completed.values("food_post__donor").distinct().count()
        orphanages_served = completed.values("recipient").distinct().count()
        co2_prevented = round(total_meals * CO2_KG_PER_MEAL, 1)
        stats = {
            "total_meals": total_meals,
            "active_donors": active_donors,
            "orphanages_served": orphanages_served,
            "co2_prevented": co2_prevented,
        }
        cache.set(cache_key, stats, timeout=300)  # 5 minutes cache
    return stats


def get_user_stats(user) -> dict:
    """
    Retrieves user-specific metrics for hotels or orphanages.
    """
    if user.is_hotel():
        total_posts = FoodPost.objects.filter(donor=user).count()
        completed = Order.objects.filter(
            food_post__donor=user, status=Order.Status.COMPLETED
        )
        completed_count = completed.count()
        total_meals = (
            completed.aggregate(total=Sum("food_post__quantity"))["total"] or 0
        )
        completion_pct = round(
            (completed_count / total_posts * 100) if total_posts > 0 else 0, 1
        )
        co2_prevented = round(total_meals * CO2_KG_PER_MEAL, 1)
        return {
            "role": "hotel",
            "total_posts": total_posts,
            "completed_count": completed_count,
            "total_meals": total_meals,
            "completion_pct": completion_pct,
            "co2_prevented": co2_prevented,
        }
    else:
        completed = Order.objects.filter(recipient=user, status=Order.Status.COMPLETED)
        total_meals = (
            completed.aggregate(total=Sum("food_post__quantity"))["total"] or 0
        )
        unique_donors = completed.values("food_post__donor").distinct().count()
        return {
            "role": "orphanage",
            "total_meals": total_meals,
            "unique_donors": unique_donors,
        }
