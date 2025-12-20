from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from .models import Alert, AlertType, AlertSubscription, UserAlertReceipt
from .forms import AlertForm
from datetime import datetime, timedelta

# List all alerts
def alert_list(request):
    active_alerts = Alert.objects.filter(
        is_active=True,
        valid_until__gte=timezone.now()
    ).order_by('-issued_at')
    
    expired_alerts = Alert.objects.filter(
        is_active=True,
        valid_until__lt=timezone.now()
    ).order_by('-issued_at')[:10]
    
    alert_types = AlertType.objects.all()
    
    # Calculate statistics for template
    total_active = active_alerts.count()
    warning_count = active_alerts.filter(severity='warning').count()
    danger_count = active_alerts.filter(severity='danger').count()
    expired_count = expired_alerts.count()
    
    context = {
        'active_alerts': active_alerts,
        'expired_alerts': expired_alerts,
        'alert_types': alert_types,
        'total_active': total_active,
        'warning_count': warning_count,
        'danger_count': danger_count,
        'expired_count': expired_count,
    }
    return render(request, 'alerts/alert_list.html', context)

# Alert details
def alert_detail(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    
    # Mark as read if user is logged in
    if request.user.is_authenticated:
        UserAlertReceipt.objects.get_or_create(
            user=request.user,
            alert=alert,
            received_via='web',
            defaults={'acknowledged': True, 'acknowledged_at': timezone.now()}
        )
    
    context = {
        'alert': alert,
    }
    return render(request, 'alerts/alert_detail.html', context)

# Create new alert (for institutions)
@login_required
def create_alert(request):
    if request.user.user_type != 'institution':
        messages.error(request, 'Seules les institutions peuvent créer des alertes.')
        return redirect('alerts:alert_list')
    
    if request.method == 'POST':
        form = AlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.issued_by = request.user
            alert.is_active = True
            alert.save()
            
            # Create receipt for creator
            UserAlertReceipt.objects.create(
                user=request.user,
                alert=alert,
                received_via='system',
                acknowledged=True,
                acknowledged_at=timezone.now()
            )
            
            messages.success(request, 'Alerte créée avec succès!')
            return redirect('alerts:alert_detail', alert_id=alert.id)
    else:
        form = AlertForm()
    
    context = {
        'form': form,
    }
    return render(request, 'alerts/create_alert.html', context)

# User alert subscriptions
@login_required
def my_subscriptions(request):
    subscriptions = AlertSubscription.objects.filter(user=request.user)
    all_types = AlertType.objects.all()
    
    if request.method == 'POST':
        # Update subscriptions
        for alert_type in all_types:
            receive_sms = request.POST.get(f'sms_{alert_type.id}') == 'on'
            receive_email = request.POST.get(f'email_{alert_type.id}') == 'on'
            receive_push = request.POST.get(f'push_{alert_type.id}') == 'on'
            
            subscription, created = AlertSubscription.objects.get_or_create(
                user=request.user,
                alert_type=alert_type,
                defaults={
                    'receive_sms': receive_sms,
                    'receive_email': receive_email,
                    'receive_push': receive_push,
                }
            )
            
            if not created:
                subscription.receive_sms = receive_sms
                subscription.receive_email = receive_email
                subscription.receive_push = receive_push
                subscription.save()
        
        messages.success(request, 'Préférences de notifications mises à jour!')
        return redirect('alerts:my_subscriptions')
    
    context = {
        'subscriptions': subscriptions,
        'alert_types': all_types,
    }
    return render(request, 'alerts/my_subscriptions.html', context)

# Emergency alert (quick creation)
@login_required
def emergency_alert(request):
    if request.user.user_type != 'institution':
        messages.error(request, 'Accès réservé aux institutions.')
        return redirect('alerts:alert_list')
    
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        alert_type_id = request.POST.get('alert_type')
        severity = request.POST.get('severity', 'danger')
        affected_areas = request.POST.get('affected_areas', '')
        instructions = request.POST.get('instructions', '')
        
        if title and description and alert_type_id:
            try:
                alert_type = AlertType.objects.get(id=alert_type_id)
                alert = Alert.objects.create(
                    alert_type=alert_type,
                    title=title,
                    description=description,
                    severity=severity,
                    affected_areas=affected_areas,
                    instructions=instructions,
                    issued_by=request.user,
                    valid_until=timezone.now() + timedelta(hours=24),
                    is_active=True,
                    source=request.user.institution_profile.official_name if hasattr(request.user, 'institution_profile') else 'Institution'
                )
                
                messages.success(request, 'Alerte d\'urgence envoyée!')
                return redirect('alerts:alert_detail', alert_id=alert.id)
            except AlertType.DoesNotExist:
                messages.error(request, 'Type d\'alerte invalide.')
    
    alert_types = AlertType.objects.all()
    context = {
        'alert_types': alert_types,
    }
    return render(request, 'alerts/emergency_alert.html', context)

# Mark alert as read
@login_required
def mark_as_read(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    
    receipt, created = UserAlertReceipt.objects.get_or_create(
        user=request.user,
        alert=alert,
        received_via='web'
    )
    
    if not receipt.acknowledged:
        receipt.acknowledged = True
        receipt.acknowledged_at = timezone.now()
        receipt.save()
        messages.success(request, 'Alerte marquée comme lue.')
    
    return redirect('alerts:alert_list')

# Alert statistics
def alert_stats(request):
    # Alerts by type
    type_stats = Alert.objects.values('alert_type__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Alerts by severity
    severity_stats = Alert.objects.values('severity').annotate(
        count=Count('id')
    ).order_by('severity')
    
    # Recent alerts (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_alerts = Alert.objects.filter(
        issued_at__gte=thirty_days_ago
    ).count()
    
    # Active alerts
    active_alerts = Alert.objects.filter(
        is_active=True,
        valid_until__gte=timezone.now()
    ).count()
    
    context = {
        'type_stats': list(type_stats),
        'severity_stats': list(severity_stats),
        'recent_alerts': recent_alerts,
        'active_alerts': active_alerts,
        'total_alerts': Alert.objects.count(),
    }
    return render(request, 'alerts/stats.html', context)