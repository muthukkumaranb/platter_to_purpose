from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.api.serializers import OrderSerializer
from apps.orders.services import claim_food, verify_pickup, withdraw_order


class ClaimFoodView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, food_id, *args, **kwargs):
        order = claim_food(request.user, food_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VerifyPickupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, token, *args, **kwargs):
        order = verify_pickup(token, request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WithdrawOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        withdraw_order(pk, request.user)
        return Response(
            {"message": "Order successfully withdrawn."},
            status=status.HTTP_204_NO_CONTENT,
        )
