from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.db.models import F

from .forms import (
    UserRegistrationForm,
    CitizenProfileForm,
    InstitutionProfileForm,
    ProfileForm,
    NotificationForm,
    CitizenProfile,
)

from .models import User, CitizenProfile, InstitutionProfile, UserNotificationSettings
from incidents.models import Incident
from alerts.models import Alert
from .chatbot import ollama_chat


def leaderboard(request):
    citizens = CitizenProfile.objects.select_related("user").order_by("-points")[:20]
    return render(request, "core/leaderboard.html", {"citizens": citizens})


def api_incidents(request):
    incidents = Incident.objects.all().values(
        "id", "title", "latitude", "longitude", "radius"
    )
    return JsonResponse(list(incidents), safe=False)


@csrf_exempt
def api_chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        msg = data.get("message", "")

        if not msg.strip():
            return JsonResponse({"reply": "Écris quelque chose 🙂"})

        reply = ollama_chat(msg)
        return JsonResponse({"reply": reply})

    return JsonResponse({"error": "Only POST allowed"}, status=405)


def home(request):
    total_incidents = Incident.objects.count()
    total_alerts = Alert.objects.filter(is_active=True).count()

    context = {
        "total_incidents": total_incidents,
        "total_alerts": total_alerts,
    }
    return render(request, "core/home.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue {username}!")
                next_url = request.GET.get("next", "home")
                return redirect(next_url)
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()

    return render(request, "core/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect("home")


# ✅✅ Register Citizen (FIXED)
def register_citizen(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        citizen_form = CitizenProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and citizen_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = "citizen"
            user.save()

            citizen_profile = citizen_form.save(commit=False)
            citizen_profile.user = user
            citizen_profile.save()

            login(request, user)
            messages.success(request, "✅ Votre compte citoyen a été créé avec succès!")
            return redirect("home")

    else:
        user_form = UserRegistrationForm()
        citizen_form = CitizenProfileForm()

    return render(
        request,
        "core/register_citizen.html",
        {
            "user_form": user_form,
            "citizen_form": citizen_form,
        },
    )


# ✅✅ Register Institution (FIXED)
def register_institution(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        institution_form = InstitutionProfileForm(request.POST)

        if user_form.is_valid() and institution_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = "institution"
            user.save()

            institution_profile = institution_form.save(commit=False)
            institution_profile.user = user
            institution_profile.save()

            login(request, user)
            messages.success(request, "✅ Votre compte institution a été créé avec succès!")
            return redirect("home")

    else:
        user_form = UserRegistrationForm()
        institution_form = InstitutionProfileForm()

    return render(
        request,
        "core/register_institution.html",
        {
            "user_form": user_form,
            "institution_form": institution_form,
        },
    )


@login_required
def profile(request):
    user = request.user

    # ✅ Ensure the correct profile exists
    citizen_profile = None
    institution_profile = None

    if user.user_type == "citizen":
        citizen_profile, _ = CitizenProfile.objects.get_or_create(user=user)
    elif user.user_type == "institution":
        institution_profile, _ = InstitutionProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        user_form = ProfileForm(request.POST, instance=user)

        if citizen_profile:
            profile_form = CitizenProfileForm(request.POST, request.FILES, instance=citizen_profile)
        elif institution_profile:
            profile_form = InstitutionProfileForm(request.POST, request.FILES, instance=institution_profile)
        else:
            profile_form = None

        # ✅ Check validity
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()

            messages.success(request, "✅ Profil mis à jour avec succès!")
            return redirect("profile")

        else:
            print("USER FORM ERRORS:", user_form.errors)
            if profile_form:
                print("PROFILE FORM ERRORS:", profile_form.errors)

            messages.error(request, f"❌ Erreur: {user_form.errors} {profile_form.errors if profile_form else ''}")


    else:
        user_form = ProfileForm(instance=user)

        if citizen_profile:
            profile_form = CitizenProfileForm(instance=citizen_profile)
        elif institution_profile:
            profile_form = InstitutionProfileForm(instance=institution_profile)
        else:
            profile_form = None

    return render(
        request,
        "core/profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "citizen": citizen_profile,
            "institution": institution_profile,
        },
    )


def settings_view(request):
    user = request.user
    notifications, _ = UserNotificationSettings.objects.get_or_create(user=user)

    if request.method == "POST":

        if "update_profile" in request.POST:
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "✅ Email mis à jour avec succès.")
                return redirect("settings")

        elif "update_notifications" in request.POST:
            notification_form = NotificationForm(request.POST, instance=notifications)
            if notification_form.is_valid():
                notification_form.save()
                messages.success(request, "✅ Notifications enregistrées.")
                return redirect("settings")

    profile_form = ProfileForm(instance=user)
    notification_form = NotificationForm(instance=notifications)

    return render(
        request,
        "core/settings.html",
        {
            "profile_form": profile_form,
            "notification_form": notification_form,
        },
    )

def parametres(request):
    return render(request, "core/settings.html")
