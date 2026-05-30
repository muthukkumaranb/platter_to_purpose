"""
Django signals for automatic notification creation.

These signal handlers listen for saves on FoodPost and Order models
and automatically create in-app Notification records + send emails.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.food.models import FoodPost
from apps.orders.models import Order

from .models import Notification
from .utils import send_notification_email


# ──────────────────────────────────────────────────
# 1. NEW FOOD POSTED → Notify all orphanage users
# ──────────────────────────────────────────────────
@receiver(post_save, sender=FoodPost)
def notify_on_new_food_post(sender, instance, created, **kwargs):
    """
    When a hotel posts new food, create a notification for every
    orphanage user so they know food is available.
    """
    if not created:
        return  # Only trigger on new posts, not updates

    User = instance.donor.__class__  # Get the User model dynamically  # noqa: N806

    # Find all orphanage users
    orphanage_users = User.objects.filter(role="ORPHANAGE")

    for user in orphanage_users:
        # Create in-app notification
        Notification.objects.create(
            user=user,
            notification_type=Notification.Type.FOOD_POSTED,
            title=f"🍲 New food available: {instance.title}",
            message=(
                f'{instance.donor.username} has posted "{instance.title}" '
                f"({instance.quantity} servings) at {instance.location}. "
                f"Claim it before it expires!"
            ),
            related_food_post=instance,
        )

        # Send email notification
        send_notification_email(
            user=user,
            subject=f"[Platter to Purpose] New Food Available: {instance.title}",
            message=(
                f"Hi {user.username},\n\n"
                f"Great news! {instance.donor.username} has posted new food:\n\n"
                f"  Title: {instance.title}\n"
                f"  Quantity: {instance.quantity} servings\n"
                f"  Location: {instance.location}\n\n"
                f"Log in to claim it before it expires!\n\n"
                f"— Platter to Purpose"
            ),
        )


# ──────────────────────────────────────────────────
# 2. FOOD CLAIMED → Notify the donor (hotel)
# ──────────────────────────────────────────────────
@receiver(post_save, sender=Order)
def notify_on_food_claimed(sender, instance, created, **kwargs):
    """
    When an orphanage claims food (Order created), notify the
    hotel/restaurant donor that their food was claimed.
    """
    if not created:
        return  # Only trigger on new orders

    donor = instance.food_post.donor
    food_title = instance.food_post.title

    # Create in-app notification for the donor
    Notification.objects.create(
        user=donor,
        notification_type=Notification.Type.FOOD_CLAIMED,
        title=f"✅ Your food was claimed: {food_title}",
        message=(
            f'{instance.recipient.username} has claimed "{food_title}". '
            f"Please prepare it for pickup."
        ),
        related_food_post=instance.food_post,
    )

    # Send email to the donor
    send_notification_email(
        user=donor,
        subject=f"[Platter to Purpose] Your Food Was Claimed: {food_title}",
        message=(
            f"Hi {donor.username},\n\n"
            f"Good news! {instance.recipient.username} has claimed your food post "
            f'"{food_title}".\n\n'
            f"Please prepare the food for pickup.\n\n"
            f"— Platter to Purpose"
        ),
    )


# ──────────────────────────────────────────────────
# 3. PICKUP VERIFIED → Notify both donor and recipient
# ──────────────────────────────────────────────────
@receiver(pre_save, sender=Order)
def notify_on_pickup_verified(sender, instance, **kwargs):
    """
    When an order's status changes to COMPLETED (pickup verified),
    notify both the donor and the recipient.

    We use pre_save to detect the status CHANGE by comparing
    the new value with the old value from the database.
    """
    # Skip if this is a brand-new order (no pk yet)
    if not instance.pk:
        return

    # Fetch the old status from the database
    try:
        old_order = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return

    # Only trigger when status changes TO completed
    if old_order.status == instance.status:
        return  # No status change
    if instance.status != Order.Status.COMPLETED:
        return  # Changed, but not to COMPLETED

    donor = instance.food_post.donor
    recipient = instance.recipient
    food_title = instance.food_post.title

    # Notify the DONOR
    Notification.objects.create(
        user=donor,
        notification_type=Notification.Type.PICKUP_VERIFIED,
        title=f"🎉 Pickup verified: {food_title}",
        message=(
            f'The pickup for "{food_title}" has been verified. '
            f"Thank you for your donation!"
        ),
        related_food_post=instance.food_post,
    )

    # Notify the RECIPIENT
    Notification.objects.create(
        user=recipient,
        notification_type=Notification.Type.PICKUP_VERIFIED,
        title=f"🎉 Pickup verified: {food_title}",
        message=(
            f'Your pickup for "{food_title}" has been verified. '
            f"Enjoy the meal and thank the donor!"
        ),
        related_food_post=instance.food_post,
    )

    # Email both parties
    for user, role in [(donor, "donor"), (recipient, "recipient")]:
        send_notification_email(
            user=user,
            subject=f"[Platter to Purpose] Pickup Verified: {food_title}",
            message=(
                f"Hi {user.username},\n\n"
                f'The pickup for "{food_title}" has been successfully verified!\n\n'
                f"{'Thank you for your generous donation!' if role == 'donor' else 'Enjoy the meal!'}\n\n"
                f"— Platter to Purpose"
            ),
        )
