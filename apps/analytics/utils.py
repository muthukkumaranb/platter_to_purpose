"""
analytics/utils.py
──────────────────
Helper functions for the Impact Tracking Dashboard:
- CO2 calculation constant
- Badge system (pure Python, no extra model)
- Monthly impact email sender
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# CO2 Calculation
# ═══════════════════════════════════════════════════════════════════
# According to ReFED / WRAP research, each meal saved prevents
# approximately 2.5 kg of CO2 equivalent emissions (includes
# production, transport, and landfill methane).
CO2_KG_PER_MEAL = 2.5


# ═══════════════════════════════════════════════════════════════════
# Badge System
# ═══════════════════════════════════════════════════════════════════
# Each badge is a tuple: (threshold, emoji, label, description)
BADGE_DEFINITIONS = [
    (1, "🌱", "First Donation", "Made your first impact!"),
    (50, "🌟", "50 Meals Saved", "Half a century of meals!"),
    (100, "🏆", "100 Meals Saved", "Triple-digit hero!"),
    (500, "💎", "500 Meals Saved", "Diamond-level impact!"),
    (1000, "🚀", "1000 Meals Saved", "Legendary contributor!"),
]


def get_user_badges(total_meals):
    """
    Return a list of earned badges based on the user's total meal count.

    Each badge dict contains:
        - threshold: int — the meal count needed to earn this badge
        - emoji: str — the badge icon
        - label: str — short name
        - description: str — motivational description
        - earned: bool — whether the user has earned it

    Args:
        total_meals: int — the user's total completed meal count

    Returns:
        list[dict] — all badge definitions with earned status
    """
    badges = []
    for threshold, emoji, label, description in BADGE_DEFINITIONS:
        badges.append(
            {
                "threshold": threshold,
                "emoji": emoji,
                "label": label,
                "description": description,
                "earned": total_meals >= threshold,
            }
        )
    return badges


def get_next_badge(total_meals):
    """
    Return the next unearned badge and progress towards it.

    Returns:
        dict with 'badge', 'progress_pct', 'meals_remaining'
        or None if all badges are earned.
    """
    for threshold, emoji, label, description in BADGE_DEFINITIONS:
        if total_meals < threshold:
            return {
                "badge": {"emoji": emoji, "label": label, "threshold": threshold},
                "progress_pct": int((total_meals / threshold) * 100),
                "meals_remaining": threshold - total_meals,
            }
    return None  # All badges earned!


def send_monthly_impact_email(user):
    """
    Send a personalized monthly impact email to a user.

    For hotels: summarizes meals donated and CO2 prevented.
    For orphanages: summarizes meals received.

    Uses Django's console email backend in dev, so emails
    print to the terminal. Errors are logged but never crash
    the application.

    Args:
        user: User instance (must have .role attribute)

    Returns:
        bool — True if email was sent, False on failure
    """
    from datetime import timedelta

    from django.template.loader import render_to_string
    from django.utils import timezone

    from apps.orders.models import Order  # Lazy import to avoid circular deps

    # Calculate date range for "last month"
    now = timezone.now()
    first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_end = first_of_this_month - timedelta(seconds=1)
    last_month_start = last_month_end.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    if user.role == "HOTEL":
        # Hotel: count meals from their donated food posts that were completed
        completed_orders = Order.objects.filter(
            food_post__donor=user,
            status=Order.Status.COMPLETED,
            claimed_at__gte=last_month_start,
            claimed_at__lte=last_month_end,
        )
        meals = (
            completed_orders.aggregate(total=Sum("food_post__quantity"))["total"] or 0
        )
        co2 = meals * CO2_KG_PER_MEAL
        subject = f"🍽️ Your Impact Last Month — {meals} Meals Saved!"
        context = {
            "user": user,
            "role": "hotel",
            "meals": meals,
            "co2": co2,
            "month_name": last_month_start.strftime("%B %Y"),
        }
    else:
        # Orphanage: count meals received
        completed_orders = Order.objects.filter(
            recipient=user,
            status=Order.Status.COMPLETED,
            claimed_at__gte=last_month_start,
            claimed_at__lte=last_month_end,
        )
        meals = (
            completed_orders.aggregate(total=Sum("food_post__quantity"))["total"] or 0
        )
        subject = f"🏠 Your Community Received {meals} Meals Last Month!"
        context = {
            "user": user,
            "role": "orphanage",
            "meals": meals,
            "month_name": last_month_start.strftime("%B %Y"),
        }

    # Render the email template
    html_body = render_to_string("analytics/impact_email.html", context)

    try:
        send_mail(
            subject=subject,
            message="",  # Plain text fallback (empty — HTML only)
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_body,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send monthly impact email to {user.email}: {e}")
        return False
