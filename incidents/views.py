from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count  # <-- THIS LINE MUST BE HERE
from django.db.models.functions import TruncMonth
from django.utils import timezone
from .models import Incident, IncidentCategory, IncidentUpdate, InstitutionResponse
from .forms import IncidentReportForm, IncidentUpdateForm
import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from .models import Incident

def api_incidents(request):
    incidents = Incident.objects.all().order_by("-created_at")

    data = []
    for inc in incidents:
        data.append({
            "id": inc.id,
            "title": inc.title,
            "status": inc.status,
            "urgency": inc.urgency,
            "latitude": float(inc.latitude),
            "longitude": float(inc.longitude),
        })

    return JsonResponse(data, safe=False)

def incidents_map(request):
    return render(request, "incidents/incidents_map.html")

def incident_list(request):
    incidents = Incident.objects.all().order_by('-created_at')
    categories = IncidentCategory.objects.all()
    
    # Filter by category if specified
    category_id = request.GET.get('category')
    if category_id:
        incidents = incidents.filter(category_id=category_id)
    
    # Filter by city if specified
    city = request.GET.get('city')
    if city:
        incidents = incidents.filter(city__icontains=city)
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status:
        incidents = incidents.filter(status=status)
    
    # Calculate statistics
    total_count = incidents.count()
    resolved_count = incidents.filter(status='resolved').count()
    in_progress_count = incidents.filter(status='in_progress').count()
    reported_count = incidents.filter(status='reported').count()
    
    context = {
        'incidents': incidents,
        'categories': categories,
        'total_count': total_count,
        'resolved_count': resolved_count,
        'in_progress_count': in_progress_count,
        'reported_count': reported_count,
    }
    return render(request, 'incidents/incident_list.html', context)

# Report a new incident
@login_required
def report_incident(request):
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        address = request.POST.get('address', '')
        city = request.POST.get('city', 'Casablanca')
        neighborhood = request.POST.get('neighborhood', '')
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        
        # Create incident
        incident = Incident.objects.create(
            citizen=request.user,
            title=title,
            description=description,
            address=address,
            city=city,
            neighborhood=neighborhood,
            is_anonymous=is_anonymous,
            status='reported',
            urgency='medium'
        )
        
        # Handle category
        if category_id:
            try:
                category = IncidentCategory.objects.get(id=category_id)
                incident.category = category
                incident.save()
            except:
                pass
        
        # Handle file uploads
        if 'image' in request.FILES:
            incident.image = request.FILES['image']
        if 'video' in request.FILES:
            incident.video = request.FILES['video']
        if 'audio_note' in request.FILES:
            incident.audio_note = request.FILES['audio_note']
        
        # Handle location
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        if latitude and longitude:
            incident.latitude = latitude
            incident.longitude = longitude
        
        incident.save()
        
        # Create initial update
        IncidentUpdate.objects.create(
            incident=incident,
            institution=request.user,
            status='reported',
            comment='Signalement initial créé par le citoyen'
        )
        
        messages.success(request, 'Votre signalement a été enregistré avec succès!')
        return redirect('incidents:incident_detail', incident_id=incident.id)
    
    # GET request - show form
    categories = IncidentCategory.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'incidents/report_incident.html', context)

# View incident details
def incident_detail(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    updates = incident.updates.all().order_by('-created_at')
    
    # Increment view count
    incident.view_count += 1
    incident.save(update_fields=['view_count'])
    
    context = {
        'incident': incident,
        'updates': updates,
    }
    return render(request, 'incidents/incident_detail.html', context)

# Update incident (for institutions)
@login_required
def update_incident(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    
    if request.method == 'POST':
        form = IncidentUpdateForm(request.POST, instance=incident)
        comment = request.POST.get('comment', '')
        
        if form.is_valid():
            old_status = incident.status
            incident = form.save()
            
            # Create update record if status changed or comment provided
            if old_status != incident.status or comment:
                IncidentUpdate.objects.create(
                    incident=incident,
                    institution=request.user,
                    status=incident.status,
                    comment=comment or f'Statut changé à: {incident.get_status_display()}'
                )
            
            messages.success(request, 'Signalement mis à jour avec succès!')
            return redirect('incidents:incident_detail', incident_id=incident.id)
    else:
        form = IncidentUpdateForm(instance=incident)
    
    context = {
        'incident': incident,
        'form': form,
    }
    return render(request, 'incidents/update_incident.html', context)

# Add institution response
@login_required
def add_response(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    
    if request.method == 'POST':
        response_text = request.POST.get('response_text', '')
        action_plan = request.POST.get('action_plan', '')
        estimated_date = request.POST.get('estimated_completion')
        
        if response_text:
            response, created = InstitutionResponse.objects.get_or_create(
                incident=incident,
                defaults={
                    'institution': request.user,
                    'response_text': response_text,
                    'action_plan': action_plan,
                    'estimated_completion': estimated_date if estimated_date else None,
                }
            )
            
            if not created:
                response.response_text = response_text
                response.action_plan = action_plan
                response.estimated_completion = estimated_date if estimated_date else None
                response.save()
            
            # Update incident status
            incident.status = 'in_progress'
            incident.save()
            
            # Create update record
            IncidentUpdate.objects.create(
                incident=incident,
                institution=request.user,
                status='in_progress',
                comment=f'Réponse institutionnelle ajoutée: {response_text[:100]}...'
            )
            
            messages.success(request, 'Réponse ajoutée avec succès!')
        
        return redirect('incidents:incident_detail', incident_id=incident.id)
    
    context = {
        'incident': incident,
    }
    return render(request, 'incidents/add_response.html', context)

# View user's incidents
@login_required
def my_incidents(request):
    incidents = Incident.objects.filter(citizen=request.user).order_by("-created_at")

    context = {
        "incidents": incidents
    }
    return render(request, "incidents/my_incidents.html", context)

# Incident statistics
def incident_stats(request):
    """Display incident statistics"""
    try:
        # Total incidents by category
        category_stats = Incident.objects.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Incidents by status
        status_stats = Incident.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Incidents by city
        city_stats = Incident.objects.values('city').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_stats = Incident.objects.filter(
            created_at__gte=six_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Calculate average resolution time
        resolved_incidents = Incident.objects.filter(status='resolved', resolved_at__isnull=False)
        avg_resolution_time = 0
        if resolved_incidents.exists():
            total_hours = 0
            for incident in resolved_incidents:
                if incident.resolved_at and incident.created_at:
                    hours = (incident.resolved_at - incident.created_at).total_seconds() / 3600
                    total_hours += hours
            avg_resolution_time = total_hours / resolved_incidents.count()
        
        context = {
            'category_stats': list(category_stats),
            'status_stats': list(status_stats),
            'city_stats': list(city_stats),
            'monthly_stats': list(monthly_stats),
            'total_incidents': Incident.objects.count(),
            'resolved_incidents': Incident.objects.filter(status='resolved').count(),
            'avg_resolution_time': round(avg_resolution_time, 1),
        }
        return render(request, 'incidents/stats.html', context)
        
    except Exception as e:
        # Fallback if there's an error
        context = {
            'category_stats': [],
            'status_stats': [],
            'city_stats': [],
            'monthly_stats': [],
            'total_incidents': 0,
            'resolved_incidents': 0,
            'avg_resolution_time': 0,
            'error': str(e),
        }
        return render(request, 'incidents/stats.html', context)

# Quick report (simplified form for mobile)
@login_required
def quick_report(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        address = request.POST.get('address', '')
        city = request.POST.get('city', 'Casablanca')
        
        if title and description:
            incident = Incident.objects.create(
                citizen=request.user,
                title=title,
                description=description,
                address=address,
                city=city,
                status='reported',
                urgency='medium'
            )
            
            if category_id:
                try:
                    category = IncidentCategory.objects.get(id=category_id)
                    incident.category = category
                    incident.save()
                except:
                    pass
            
            messages.success(request, 'Signalement rapide enregistré!')
            return redirect('incidents:incident_detail', incident_id=incident.id)
    
    categories = IncidentCategory.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'incidents/quick_report.html', context)
from django.shortcuts import render
from django.http import JsonResponse
from ai_model.inference.classifier import ReportClassifier

def test_ai_view(request):
    """Test page to see AI in action"""
    # Initialize classifier
    classifier = ReportClassifier()
    
    # Test reports
    test_reports = [
        "Fire emergency! Building on fire, people trapped!",
        "Street light not working on Main Street",
        "Gas leak detected, strong smell of gas everywhere",
        "Garbage not collected for 2 weeks",
        "Car accident with injuries on highway",
        "Park bench needs painting",
        "Water main burst flooding the neighborhood",
        "Loud party disturbing the peace"
    ]
    
    predictions = []
    
    # Process each report - FIXED INDENTATION
    for report in test_reports:
        result = classifier.predict(report)
        urgency_score = result['urgency_score']
        
        # Calculate percentage
        percentage = int(urgency_score * 100)
        
        # Determine COLOR based on urgency score
        if urgency_score >= 0.8:  # 80%+ = RED (High urgency)
            color_class = "danger"
            bg_class = "bg-danger"
            text_class = "text-danger"
            urgency_level = "HIGH"
            icon = "🔴"
        elif urgency_score >= 0.5:  # 50-79% = ORANGE/YELLOW (Medium)
            color_class = "warning"
            bg_class = "bg-warning"
            text_class = "text-warning"
            urgency_level = "MEDIUM"
            icon = "🟡"
        else:  # 0-49% = GREEN (Low urgency)
            color_class = "success"
            bg_class = "bg-success"
            text_class = "text-success"
            urgency_level = "LOW"
            icon = "🟢"
        
        # Determine if urgent (for binary classification)
        is_urgent = result['is_urgent']
        
        predictions.append({
            'report': report,
            'is_urgent': is_urgent,
            'color_class': color_class,      # For Bootstrap classes
            'bg_class': bg_class,            # Background class
            'text_class': text_class,        # Text color class
            'urgency_level': urgency_level,  # Text label
            'icon': icon,                    # Emoji icon
            'confidence': result['confidence'],
            'urgency_score': urgency_score,
            'percentage': percentage,
            'confidence_level': result['confidence_level'],
        })
    
    # Handle form submission
    if request.method == 'POST':
        user_report = request.POST.get('report_text', '').strip()
        if user_report:
            # Analyze user's report
            user_result = classifier.predict(user_report)
            user_urgency_score = user_result['urgency_score']
            user_percentage = int(user_urgency_score * 100)
            
            # Determine color for user's report
            if user_urgency_score >= 0.8:
                user_color_class = "danger"
                user_bg_class = "bg-danger"
                user_text_class = "text-danger"
                user_urgency_level = "HIGH"
                user_icon = "🔴"
            elif user_urgency_score >= 0.5:
                user_color_class = "warning"
                user_bg_class = "bg-warning"
                user_text_class = "text-warning"
                user_urgency_level = "MEDIUM"
                user_icon = "🟡"
            else:
                user_color_class = "success"
                user_bg_class = "bg-success"
                user_text_class = "text-success"
                user_urgency_level = "LOW"
                user_icon = "🟢"
            
            user_prediction = {
                'report': user_report,
                'is_urgent': user_result['is_urgent'],
                'color_class': user_color_class,
                'bg_class': user_bg_class,
                'text_class': user_text_class,
                'urgency_level': user_urgency_level,
                'icon': user_icon,
                'confidence': user_result['confidence'],
                'urgency_score': user_urgency_score,
                'percentage': user_percentage,
                'confidence_level': user_result['confidence_level'],
                'is_user_report': True  # Flag to distinguish user's report
            }
            
            # Add user's report to the top
            predictions.insert(0, user_prediction)
    
    return render(request, 'incidents/test_ai.html', {
        'predictions': predictions,
        'title': 'AI Report Classifier'
    })