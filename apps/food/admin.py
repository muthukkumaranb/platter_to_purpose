"""
food/admin.py
─────────────
Admin configuration for FoodPost with priority window support.
"""

from datetime import timedelta

from django.contrib import admin
from django.utils import timezone

from .models import FoodPost


class PriorityWindowFilter(admin.SimpleListFilter):
    """Custom admin filter for priority window status."""

    title = "Priority Status"
    parameter_name = "priority_status"

    def lookups(self, request, model_admin):
        return (
            ("in_window", "🟢 In Priority Window"),
            ("open", "🔵 Open to All"),
            ("claimed", "🔴 Claimed"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "in_window":
            return queryset.filter(
                is_claimed=False,
                priority_window_ends__gt=now,
            )
        if self.value() == "open":
            return queryset.filter(
                is_claimed=False,
            ).exclude(priority_window_ends__gt=now)
        if self.value() == "claimed":
            return queryset.filter(is_claimed=True)
        return queryset


@admin.register(FoodPost)
class FoodPostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "donor",
        "quantity",
        "location",
        "expiry_time",
        "priority_window_ends",
        "priority_status_display",
        "is_claimed",
        "created_at",
    )
    list_filter = (PriorityWindowFilter, "is_claimed", "created_at", "donor")
    search_fields = ("title", "description", "location")
    readonly_fields = ("created_at",)
    actions = ["extend_priority_window"]

    @admin.display(description="Priority Status")
    def priority_status_display(self, obj):
        status = obj.priority_status
        if status == "priority":
            return "🟢 In Priority Window"
        elif status == "claimed":
            return "🔴 Claimed"
        return "🔵 Open to All"

    @admin.action(description="Extend priority window by 15 minutes")
    def extend_priority_window(self, request, queryset):
        now = timezone.now()
        updated = 0
        for food in queryset.filter(is_claimed=False):
            if food.priority_window_ends and food.priority_window_ends > now:
                # Extend existing window
                food.priority_window_ends += timedelta(minutes=15)
            else:
                # Re-open a new 15-min window from now
                food.priority_window_ends = now + timedelta(minutes=15)
            food.save(update_fields=["priority_window_ends"])
            updated += 1
        self.message_user(
            request, f"Extended priority window for {updated} post(s) by 15 minutes."
        )
