from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError

from apps.food.models import FoodPost
from apps.notifications.models import Notification


def post_food_donation(user, form_data, files=None) -> FoodPost:
    if user.role != "HOTEL":
        raise ValidationError("Only hotels can post food donations.")

    from apps.food.forms import FoodPostForm

    form = FoodPostForm(form_data, files)
    if not form.is_valid():
        raise ValidationError(form.errors)

    food = form.save(commit=False)
    food.donor = user
    food.save()

    # Invalidate cache for available food
    cache.delete("available_food_ids")

    # Trigger priority notifications
    User = get_user_model()  # noqa: N806
    orphanages = User.objects.filter(role="ORPHANAGE")
    notifications = []
    for orphanage in orphanages:
        notifications.append(
            Notification(
                user=orphanage,
                notification_type=Notification.Type.PRIORITY_OPEN,
                title="🍽️ Priority Claim Window Open — Act Fast!",
                message=(
                    f'{food.donor.username} just posted "{food.title}" '
                    f"— {food.quantity} servings available at {food.location}. "
                    f"You have 30 minutes to claim before it opens to everyone!"
                ),
                related_food_post=food,
            )
        )
    Notification.objects.bulk_create(notifications)

    return food
