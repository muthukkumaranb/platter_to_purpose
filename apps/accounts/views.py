from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.core.cache import cache
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm
from .models import User
from .utils import generate_otp, send_email_otp


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            demo_mode=settings.DEMO_MODE,
            demo_roles=User.Role.choices,
        )
        return context


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until OTP verified
            user.save()

            # Generate and Send OTP
            otp = generate_otp()
            email = form.cleaned_data.get("email")

            # Store validated data in session for verification step
            request.session["signup_user_id"] = user.pk
            request.session["signup_otp"] = otp

            send_email_otp(email, otp)

            messages.info(
                request, f"OTP sent to {email} (check console for demo)"
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
            messages.success(request, "Email verification successful!")
            return redirect("home")
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "accounts/verify_otp.html")


@require_POST
def demo_login(request, role):
    if not settings.DEMO_MODE:
        raise Http404

    valid_roles = {value for value, _label in User.Role.choices}
    if role not in valid_roles:
        raise Http404

    client_ip = request.META.get("REMOTE_ADDR", "unknown")
    rate_limit_key = f"demo-login:{client_ip}"
    if not cache.add(rate_limit_key, 1, timeout=60):
        request_count = cache.incr(rate_limit_key)
        if request_count > 20:
            return HttpResponse("Too many demo login attempts.", status=429)

    user = get_object_or_404(User, role=role, is_demo=True, is_active=True)
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect("dashboard")
