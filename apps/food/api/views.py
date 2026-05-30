from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from apps.food.api.serializers import FoodPostSerializer
from apps.food.models import FoodPost
from apps.food.selectors import get_available_food, get_food_by_id
from apps.food.services import post_food_donation


class FoodPostViewSet(viewsets.ModelViewSet):
    serializer_class = FoodPostSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.action == "list":
            foods = get_available_food()
            user = self.request.user
            is_orphanage = user.is_authenticated and user.is_orphanage()
            if not is_orphanage:
                now = timezone.now()
                foods = foods.filter(
                    Q(priority_window_ends__isnull=True)
                    | Q(priority_window_ends__lte=now)
                )
            return foods
        return FoodPost.objects.all()

    def get_object(self):
        pk = self.kwargs.get("pk")
        return get_food_by_id(pk)

    def create(self, request, *args, **kwargs):
        try:
            food = post_food_donation(request.user, request.data, request.FILES)
            serializer = self.get_serializer(food)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except DjangoValidationError as e:
            raise DRFValidationError(
                e.message_dict if hasattr(e, "message_dict") else e.messages
            )
