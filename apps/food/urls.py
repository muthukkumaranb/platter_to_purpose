from django.urls import path

from . import views

urlpatterns = [
    path("", views.food_list, name="food_list"),
    path("<int:pk>/", views.food_detail, name="food_detail"),
    path("post/", views.post_food, name="post_food"),
]
