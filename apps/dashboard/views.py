from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    if request.user.role == "HOTEL":
        # Show posts made by this hotel
        my_posts = request.user.food_posts.all().prefetch_related("order__feedback")
        return render(request, "dashboard/hotel_dashboard.html", {"my_posts": my_posts})
    else:
        # Show orders made by this orphanage
        my_orders = request.user.orders.all().select_related(
            "food_post", "food_post__donor"
        )
        return render(
            request, "dashboard/orphanage_dashboard.html", {"my_orders": my_orders}
        )
