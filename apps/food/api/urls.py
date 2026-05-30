from rest_framework.routers import DefaultRouter

from apps.food.api.views import FoodPostViewSet

router = DefaultRouter()
router.register("", FoodPostViewSet, basename="foodpost")

urlpatterns = router.urls
