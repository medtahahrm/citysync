# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import (
    UserRegistrationForm,
    CitizenProfileForm,
    InstitutionProfileForm,
    ProfileForm,
    NotificationForm,
)   
from .models import User, CitizenProfile, InstitutionProfile, UserNotificationSettings
from incidents.models import Incident
from alerts.models import Alert
import os, json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot import ollama_chat

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

# Home page
def home(request):
    # PUBLIC stats (VISIBLE EVEN WHEN LOGGED OUT)
    total_incidents = Incident.objects.count()
    total_alerts = Alert.objects.filter(is_active=True).count()

    context = {
        "total_incidents": total_incidents,
        "total_alerts": total_alerts,
    }
    return render(request, "core/home.html", context)

# Login view
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('home')

# Register Citizen
def register_citizen(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        citizen_form = CitizenRegistrationForm(request.POST)
        
        if user_form.is_valid() and citizen_form.is_valid():
            # Create user
            user = user_form.save(commit=False)
            user.user_type = 'citizen'
            user.set_password(user_form.cleaned_data['password1'])
            user.save()
            
            # Create citizen profile
            citizen_profile = citizen_form.save(commit=False)
            citizen_profile.user = user
            citizen_profile.save()
            
            # Auto login
            login(request, user)
            messages.success(request, 'Votre compte citoyen a été créé avec succès!')
            return redirect('home')
    else:
        user_form = UserRegistrationForm()
        citizen_form = CitizenProfileForm()
    
    context = {
        'user_form': user_form,
        'citizen_form': citizen_form,
    }
    return render(request, 'core/register_citizen.html', context)

# Register Institution
def register_institution(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        institution_form = InstitutionRegistrationForm(request.POST)
        
        if user_form.is_valid() and institution_form.is_valid():
            # Create user
            user = user_form.save(commit=False)
            user.user_type = 'institution'
            user.set_password(user_form.cleaned_data['password1'])
            user.save()
            
            # Create institution profile
            institution_profile = institution_form.save(commit=False)
            institution_profile.user = user
            institution_profile.save()
            
            # Auto login
            login(request, user)
            messages.success(request, 'Votre compte institution a été créé avec succès!')
            return redirect('home')
    else:
        user_form = UserRegistrationForm()
        institution_form = InstitutionProfileForm()
    
    context = {
        'user_form': user_form,
        'institution_form': institution_form,
    }
    return render(request, 'core/register_institution.html', context)

# Profile view
@login_required
def profile(request):
    user = request.user
    citizen_profile = CitizenProfile.objects.get(user=user)

    if request.method == "POST":
        user_form = ProfileForm(request.POST, instance=user)
        citizen_form = CitizenProfileForm(
            request.POST,
            request.FILES,
            instance=citizen_profile,
        )

        if user_form.is_valid() and citizen_form.is_valid():
            user_form.save()
            citizen_form.save()

            messages.success(request, "Profil mis à jour avec succès ✨")
            return redirect("profile")
    else:
        user_form = ProfileForm(instance=user)
        citizen_form = CitizenProfileForm(instance=citizen_profile)

    return render(
        request,
        "core/profile.html",
        {
            "user_form": user_form,
            "citizen_form": citizen_form,
            "citizen": citizen_profile,
        },
    )
    
def parametres(request):
    return render(request, 'core/parametes.html')  # Change to match your filename

def mon_profil(request):
    """My Profile page view (if different from profile)"""
    return render(request, 'core/mon_profil.html')

def settings_view(request):
    user = request.user
    notifications, _ = UserNotificationSettings.objects.get_or_create(user=user)

    # SUCCESS AFTER PASSWORD CHANGE
    if request.GET.get("password_changed") == "1":
        messages.success(
            request,
            "✅ Mot de passe mis à jour avec succès."
        )

    if request.method == "POST":

        # PROFILE UPDATE
        if "update_profile" in request.POST:
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Email mis à jour avec succès.")
                return redirect("settings")

        # NOTIFICATIONS UPDATE
        elif "update_notifications" in request.POST:
            notification_form = NotificationForm(
                request.POST, instance=notifications
            )
            if notification_form.is_valid():
                notification_form.save()
                messages.success(
                    request,
                    "Préférences de notifications enregistrées."
                )
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