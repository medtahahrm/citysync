from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
from incidents.models import Incident, IncidentCategory
from alerts.models import Alert
from core.models import User

@login_required
def institution_dashboard(request):
    if request.user.user_type != 'institution':
        return render(request, 'dashboard/access_denied.html')
    
    # Get institution's jurisdiction area
    jurisdiction = ''
    if hasattr(request.user, 'institution_profile'):
        jurisdiction = request.user.institution_profile.jurisdiction_area
    
    # Get incidents in jurisdiction
    if jurisdiction:
        incidents = Incident.objects.filter(
            Q(city__icontains=jurisdiction) | 
            Q(address__icontains=jurisdiction)
        )
    else:
        incidents = Incident.objects.all()
    
    # Statistics
    total_incidents = incidents.count()
    resolved_incidents = incidents.filter(status='resolved').count()
    active_incidents = incidents.exclude(status__in=['resolved', 'closed']).count()
    
    # Recent incidents
    recent_incidents = incidents.order_by('-created_at')[:5]
    
    # Incidents by category
    category_stats = incidents.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Incidents by status
    status_stats = incidents.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Response time (placeholder)
    avg_response_time = 24  # hours
    
    context = {
        'total_incidents': total_incidents,
        'resolved_incidents': resolved_incidents,
        'active_incidents': active_incidents,
        'recent_incidents': recent_incidents,
        'category_stats': list(category_stats),
        'status_stats': list(status_stats),
        'avg_response_time': avg_response_time,
        'jurisdiction': jurisdiction or 'Toutes zones',
    }
    return render(request, 'dashboard/institution_dashboard.html', context)

@login_required
def citizen_dashboard(request):
    if request.user.user_type != 'citizen':
        return render(request, 'dashboard/access_denied.html')
    
    # Get citizen's incidents
    incidents = Incident.objects.filter(citizen=request.user)
    
    # Statistics
    total_reported = incidents.count()
    resolved = incidents.filter(status='resolved').count()
    in_progress = incidents.filter(status='in_progress').count()
    
    # Recent activity
    recent_activity = incidents.order_by('-created_at')[:5]
    
    # Alerts for citizen's city
    city_alerts = Alert.objects.filter(
        is_active=True,
        affected_areas__icontains=request.user.city
    ).order_by('-issued_at')[:3]
    
    context = {
        'total_reported': total_reported,
        'resolved': resolved,
        'in_progress': in_progress,
        'recent_activity': recent_activity,
        'city_alerts': city_alerts,
        'user_city': request.user.city,
    }
    return render(request, 'dashboard/citizen_dashboard.html', context)

def public_dashboard(request):
    # Public statistics
    total_incidents = Incident.objects.count()
    resolved_incidents = Incident.objects.filter(status='resolved').count()
    active_alerts = Alert.objects.filter(is_active=True).count()
    total_citizens = User.objects.filter(user_type='citizen').count()
    
    # Top cities with incidents
    top_cities = Incident.objects.values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Recent public incidents
    recent_incidents = Incident.objects.filter(
        is_anonymous=False
    ).order_by('-created_at')[:5]
    
    context = {
        'total_incidents': total_incidents,
        'resolved_incidents': resolved_incidents,
        'active_alerts': active_alerts,
        'total_citizens': total_citizens,
        'top_cities': list(top_cities),
        'recent_incidents': recent_incidents,
    }
    return render(request, 'dashboard/public_dashboard.html', context)