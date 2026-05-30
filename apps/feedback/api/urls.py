from django.urls import path

from apps.feedback.api.views import LeaveFeedbackView

urlpatterns = [
    path("<int:order_id>/", LeaveFeedbackView.as_view(), name="api_leave_feedback"),
]
