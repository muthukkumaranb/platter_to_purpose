from django.urls import path

from apps.analytics.api.views import PersonalImpactStatsView, PublicImpactStatsView

urlpatterns = [
    path("public/", PublicImpactStatsView.as_view(), name="api_public_stats"),
    path("me/", PersonalImpactStatsView.as_view(), name="api_personal_stats"),
]
