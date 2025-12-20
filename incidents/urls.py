from django.urls import path
from . import views

app_name = 'incidents'

urlpatterns = [
    # Public views
    path('', views.incident_list, name='incident_list'),
    path('stats/', views.incident_stats, name='incident_stats'),
    path('<int:incident_id>/', views.incident_detail, name='incident_detail'),
    
    # Citizen views (require login)
    path('report/', views.report_incident, name='report_incident'),  # ADD THIS LINE
    path('quick-report/', views.quick_report, name='quick_report'),
    path('my-incidents/', views.my_incidents, name='my_incidents'),
    
    # Institution views (require login)
    path('<int:incident_id>/update/', views.update_incident, name='update_incident'),
    path('<int:incident_id>/respond/', views.add_response, name='add_response'),
]