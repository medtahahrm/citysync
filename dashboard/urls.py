from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('institution/', views.institution_dashboard, name='institution_dashboard'),
    path('citizen/', views.citizen_dashboard, name='citizen_dashboard'),
    path('public/', views.public_dashboard, name='public_dashboard'),
]