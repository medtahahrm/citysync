from django.db import models
from core.models import User

# Alert Types
class AlertType(models.Model):
    name = models.CharField(max_length=100)  # Séisme, Inondation, Incendie, etc.
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    color = models.CharField(max_length=20, default='#FF0000')
    icon = models.CharField(max_length=50, blank=True)
    sound_alert = models.FileField(upload_to='alert_sounds/', null=True, blank=True)
    
    def __str__(self):
        return self.name

# Main Alert Model
class Alert(models.Model):
    SEVERITY_LEVELS = (
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('danger', 'Danger'),
        ('critical', 'Critique'),
    )
    
    # Alert Information
    alert_type = models.ForeignKey(AlertType, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='warning')
    
    # Location
    affected_areas = models.TextField()  # JSON or comma-separated areas
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    radius_km = models.FloatField(null=True, blank=True)  # Affected radius in km
    
    # Timing
    issued_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Source
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=100, blank=True)  # Météo Maroc, Protection Civile, etc.
    
    # Instructions
    instructions = models.TextField(blank=True)
    emergency_numbers = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_severity_display()}"
    
    class Meta:
        ordering = ['-issued_at']

# Alert Subscription
class AlertSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_subscriptions')
    alert_type = models.ForeignKey(AlertType, on_delete=models.CASCADE)
    receive_sms = models.BooleanField(default=False)
    receive_email = models.BooleanField(default=True)
    receive_push = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'alert_type']

# User Alert Receipt
class UserAlertReceipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    received_via = models.CharField(max_length=20)  # email, sms, push
    received_at = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'alert', 'received_via']