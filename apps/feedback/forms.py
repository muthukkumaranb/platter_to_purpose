from django import forms

from .models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(
                attrs={"min": 1, "max": 5, "class": "form-control"}
            ),
            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "How was the food and pickup experience?",
                }
            ),
        }
