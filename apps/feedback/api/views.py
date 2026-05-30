from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.feedback.api.serializers import FeedbackSerializer
from apps.orders.models import Order


class LeaveFeedbackView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, pk=order_id)
        if order.recipient != request.user:
            return Response(
                {
                    "error": "unauthorized",
                    "detail": "You cannot submit feedback for this order.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if hasattr(order, "feedback"):
            raise ValidationError("Feedback already exists for this order.")

        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order=order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
