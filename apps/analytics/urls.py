"""
analytics/urls.py
─────────────────
URL patterns for the Impact Tracking Dashboard.
"""

from django.urls import path

from . import views

urlpatterns = [
    # Public impact page — no login required
    path("", views.public_impact, name="public_impact"),
    # Live feed API — returns JSON for auto-refresh
    path("api/live-feed/", views.live_feed_api, name="live_feed_api"),
    # Personal impact page — login required
    path("personal/", views.personal_impact, name="personal_impact"),
]
