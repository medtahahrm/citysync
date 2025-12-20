from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    User,
    CitizenProfile,
    InstitutionProfile,
    UserNotificationSettings,
)

# ==========================
# CUSTOM USER ADMIN
# ==========================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("id",)
    list_display = (
        "username",
        "email",
        "user_type",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = ("user_type", "is_active", "is_staff")
    search_fields = ("username", "email")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Informations personnelles"), {"fields": ("email", "phone_number", "city")}),
        (_("Permissions"), {"fields": ("user_type", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Dates importantes"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "user_type",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )


# ==========================
# CITIZEN PROFILE ADMIN
# ==========================

@admin.register(CitizenProfile)
class CitizenProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "profession",
        "city_display",
        "verified",
    )
    list_filter = ("verified",)
    search_fields = ("user__username", "user__email", "profession")
    readonly_fields = ("user",)

    def city_display(self, obj):
        return obj.user.city
    city_display.short_description = "Ville"


# ==========================
# INSTITUTION PROFILE ADMIN
# ==========================

@admin.register(InstitutionProfile)
class InstitutionProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "official_name",
        "institution_type",
        "department",
    )
    search_fields = ("official_name", "department", "user__username")
    readonly_fields = ("user",)


# ==========================
# NOTIFICATION SETTINGS ADMIN
# ==========================

@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "email_notifications",
        "incident_alerts",
    )
    list_filter = ("email_notifications", "incident_alerts")
    search_fields = ("user__username", "user__email")
