from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.api.serializers import NotificationSerializer
from apps.notifications.models import Notification


from apps.notifications.selectors import get_user_notifications

class NotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        notifications = get_user_notifications(request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
