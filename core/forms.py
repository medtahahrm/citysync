from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    User,
    CitizenProfile,
    InstitutionProfile,
    UserNotificationSettings,
)

# =========================
# USER REGISTRATION
# =========================

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=False)
    city = forms.CharField(required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "phone_number",
            "city",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


# =========================
# CITIZEN PROFILE FORM
# =========================

class CitizenProfileForm(forms.ModelForm):
    class Meta:
        model = CitizenProfile
        fields = (
            "profession",
            "date_of_birth",
            "emergency_contact",
            "profile_picture",
        )
        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "profession": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "emergency_contact": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }


# =========================
# INSTITUTION PROFILE FORM
# =========================

class InstitutionProfileForm(forms.ModelForm):
    class Meta:
        model = InstitutionProfile
        fields = (
            "official_name",
            "institution_type",
            "department",
        )
        widgets = {
            "official_name": forms.TextInput(attrs={"class": "form-control"}),
            "institution_type": forms.Select(attrs={"class": "form-select"}),
            "department": forms.TextInput(attrs={"class": "form-control"}),
        }


# =========================
# BASIC PROFILE (EMAIL)
# =========================

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            )
        }


# =========================
# NOTIFICATIONS
# =========================

class NotificationForm(forms.ModelForm):
    class Meta:
        model = UserNotificationSettings
        fields = ("email_notifications", "incident_alerts")
        widgets = {
            "email_notifications": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "incident_alerts": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
