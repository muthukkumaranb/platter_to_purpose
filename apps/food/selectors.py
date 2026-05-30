from django.core.cache import cache
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.food.models import FoodPost


def get_available_food(
    user=None,
    q: str = None,
    location: str = None,
    min_qty: int = None,
    sort: str = "newest",
) -> QuerySet[FoodPost]:
    """
    Retrieves available food posts, applying role-based priority window checks, search queries, filters, and sort options.
    Caches the list of available IDs for 60 seconds if no filters are applied.
    """
    now = timezone.now()

    # If no filtering is applied, we can use cached IDs
    if not (q or location or min_qty or sort != "newest"):
        cache_key = "available_food_ids"
        food_ids = cache.get(cache_key)
        if food_ids is None:
            food_ids = list(FoodPost.objects.available().values_list("id", flat=True))
            cache.set(cache_key, food_ids, timeout=60)
        foods = FoodPost.objects.filter(id__in=food_ids).select_related("donor")
    else:
        foods = FoodPost.objects.available().select_related("donor")

    # Priority Window filtering (role-based)
    is_orphanage = user.is_authenticated and user.is_orphanage() if user else False
    if not is_orphanage:
        foods = foods.filter(
            Q(priority_window_ends__isnull=True) | Q(priority_window_ends__lte=now)
        )

    if q:
        foods = foods.filter(Q(title__icontains=q) | Q(description__icontains=q))

    if location:
        foods = foods.filter(location__icontains=location)

    if min_qty:
        try:
            min_qty_int = int(min_qty)
            if min_qty_int > 0:
                foods = foods.filter(quantity__gte=min_qty_int)
        except ValueError:
            pass

    if sort == "expiry":
        foods = foods.order_by("expiry_time")
    elif sort == "quantity":
        foods = foods.order_by("-quantity")
    else:
        foods = foods.order_by("-created_at")

    return foods


def get_food_by_id(pk: int) -> FoodPost:
    return get_object_or_404(FoodPost, pk=pk)


def get_hotel_posts(user) -> QuerySet[FoodPost]:
    return FoodPost.objects.by_donor(user)
