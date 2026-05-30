from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.selectors import get_platform_stats, get_user_stats
from apps.analytics.services import award_badges


class PublicImpactStatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        stats = get_platform_stats()
        return Response(stats, status=status.HTTP_200_OK)


class PersonalImpactStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        stats = get_user_stats(request.user)
        badges = award_badges(request.user)
        stats["badges"] = badges
        return Response(stats, status=status.HTTP_200_OK)
