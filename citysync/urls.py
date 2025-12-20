from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- OVERRIDE PASSWORD CHANGE (IMPORTANT) ---
    path(
        "accounts/password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            success_url="/settings/?password_changed=1"
        ),
        name="password_change",
    ),

    # --- KEEP OTHER AUTH URLS ---
    path("accounts/", include("django.contrib.auth.urls")),

    # --- APP URLS ---
    path('', include('core.urls')),
    path('incidents/', include('incidents.urls')),
    path('alerts/', include('alerts.urls')),
    path('dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
