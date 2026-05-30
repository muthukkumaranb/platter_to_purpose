from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("food_post", "recipient", "status", "claimed_at")
    list_filter = ("status", "claimed_at")
    search_fields = ("food_post__title", "recipient__username")
