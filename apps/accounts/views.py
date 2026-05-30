from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomUserCreationForm
from .models import User
from .utils import generate_otp, send_whatsapp_otp


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until OTP verified
            user.save()

            # Generate and Send OTP
            otp = generate_otp()
            phone_number = form.cleaned_data.get("phone")

            # Store validated data in session for verification step
            request.session["signup_user_id"] = user.pk
            request.session["signup_otp"] = otp

            send_whatsapp_otp(phone_number, otp)

            messages.info(
                request, f"OTP sent to {phone_number} (check console for demo)"
            )
            return redirect("verify_otp")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        generated_otp = request.session.get("signup_otp")
        user_id = request.session.get("signup_user_id")

        if not generated_otp or not user_id:
            messages.error(request, "Session expired. Please sign up again.")
            return redirect("signup")

        if entered_otp == generated_otp:
            user = get_object_or_404(User, pk=user_id)
            user.is_active = True
            user.save()

            # Clean up session
            del request.session["signup_otp"]
            del request.session["signup_user_id"]

            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Phone verification successful!")
            return redirect("home")
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "accounts/verify_otp.html")
