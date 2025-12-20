from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    # Public views
    path('', views.alert_list, name='alert_list'),
    path('stats/', views.alert_stats, name='alert_stats'),
    path('<int:alert_id>/', views.alert_detail, name='alert_detail'),
    
    # User views (require login)
    path('subscriptions/', views.my_subscriptions, name='my_subscriptions'),
    path('<int:alert_id>/read/', views.mark_as_read, name='mark_as_read'),
    
    # Institution views
    path('create/', views.create_alert, name='create_alert'),
    path('emergency/', views.emergency_alert, name='emergency_alert'),
]