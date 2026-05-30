from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("accounts/", include("apps.accounts.urls")),
    path("food/", include("apps.food.urls")),
    path("orders/", include("apps.orders.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("feedback/", include("apps.feedback.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("impact/", include("apps.analytics.urls")),
    path("404/", TemplateView.as_view(template_name="404.html")),
    # API v1 routes
    path("api/v1/auth/", include("apps.accounts.api.urls")),
    path("api/v1/food/", include("apps.food.api.urls")),
    path("api/v1/orders/", include("apps.orders.api.urls")),
    path("api/v1/feedback/", include("apps.feedback.api.urls")),
    path("api/v1/analytics/", include("apps.analytics.api.urls")),
    path("api/v1/notifications/", include("apps.notifications.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Django Debug Toolbar
    try:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass
