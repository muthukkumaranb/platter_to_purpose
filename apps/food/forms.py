from django import forms

from .models import FoodPost


class FoodPostForm(forms.ModelForm):
    class Meta:
        model = FoodPost
        fields = [
            "title",
            "description",
            "quantity",
            "location",
            "expiry_time",
            "image",
        ]
        widgets = {
            "expiry_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
