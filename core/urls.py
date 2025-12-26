# core/urls.py
from django.urls import path
from . import views
from .views import api_chat

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/citizen/', views.register_citizen, name='register_citizen'),
    path("settings/", views.settings_view, name="settings"),
    path('register/institution/', views.register_institution, name='register_institution'),
    path("profile/", views.profile, name="profile"),
    # ADD THESE LINES:
    path('parametres/', views.parametres, name='parametres'),  # Settings page
    path('mon-profil/', views.mon_profil, name='mon_profil'),  # If needed
    path("api/chat/", views.api_chat, name="api_chat"),
    path("api/chat/", api_chat, name="api_chat"),
    
]