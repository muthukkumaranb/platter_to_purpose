from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "role", "phone", "address")
        widgets = {
            "role": forms.RadioSelect(attrs={"class": "role-select"}),
        }
