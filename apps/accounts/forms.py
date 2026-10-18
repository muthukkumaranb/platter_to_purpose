from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "role", "phone", "address")
        widgets = {
            "role": forms.RadioSelect(attrs={"class": "role-select"}),
        }
