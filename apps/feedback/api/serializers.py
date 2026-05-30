from rest_framework import serializers

from apps.feedback.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ("id", "rating", "comment", "created_at")
