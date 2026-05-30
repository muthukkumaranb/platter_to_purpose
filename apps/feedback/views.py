from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.orders.models import Order

from .forms import FeedbackForm


@login_required
def submit_feedback(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    # Only recipient can submit feedback
    if request.user != order.recipient:
        return redirect("dashboard")

    # Check if feedback already exists
    try:
        feedback = order.feedback
    except Order.feedback.RelatedObjectDoesNotExist:
        feedback = None

    if request.method == "POST":
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.order = order
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect("dashboard")
    else:
        form = FeedbackForm(instance=feedback)

    return render(
        request, "feedback/submit_feedback.html", {"form": form, "order": order}
    )
