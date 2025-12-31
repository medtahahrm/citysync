from django.db import models
from core.models import User

# Incident Categories
class IncidentCategory(models.Model):
    PRIORITY_CHOICES = (
        (1, 'Très Basse'),
        (2, 'Basse'),
        (3, 'Moyenne'),
        (4, 'Haute'),
        (5, 'Critique'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    priority_level = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    response_time_hours = models.IntegerField(default=24)  # Expected response time
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Incident Categories"

# Main Incident Model
class Incident(models.Model):
    STATUS_CHOICES = (
        ('reported', 'Signalé'),
        ('verified', 'Vérifié'),
        ('in_progress', 'En cours de traitement'),
        ('resolved', 'Résolu'),
        ('closed', 'Fermé'),
        ('false_alarm', 'Fausse alerte'),
    )
    
    URGENCY_LEVELS = (
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
        ('critical', 'Critique'),
    )
    
    # Basic Information
    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_incidents')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(IncidentCategory, on_delete=models.SET_NULL, null=True, blank=True)
    urgency = models.CharField(max_length=20, choices=URGENCY_LEVELS, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    
    # Location Data
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100, blank=True)
    
    # Multimedia
    image = models.ImageField(upload_to='incident_images/', null=True, blank=True)
    video = models.FileField(upload_to='incident_videos/', null=True, blank=True)
    audio_note = models.FileField(upload_to='incident_audio/', null=True, blank=True)
    
    # AI Processing Fields
    ai_analysis = models.JSONField(null=True, blank=True)  # Store AI results
    ai_category = models.ForeignKey(IncidentCategory, on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='ai_categorized_incidents')
    ai_urgency_score = models.FloatField(null=True, blank=True)
    ai_confidence = models.FloatField(null=True, blank=True)  # AI confidence level (0-1)
    is_ai_verified = models.BooleanField(default=False)
    ai_keywords = models.TextField(blank=True)  # Extracted keywords
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    is_anonymous = models.BooleanField(default=False)
    upvotes = models.IntegerField(default=0)  # Citizens can upvote important incidents
    view_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['-created_at']

# Incident Updates/Status Changes
class IncidentUpdate(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='updates')
    institution = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    comment = models.TextField()
    attachment = models.FileField(upload_to='update_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Update for {self.incident.title}"

# Institution Response
class InstitutionResponse(models.Model):
    incident = models.OneToOneField(Incident, on_delete=models.CASCADE, related_name='official_response')
    institution = models.ForeignKey(User, on_delete=models.CASCADE)
    response_text = models.TextField()
    action_plan = models.TextField(blank=True)
    estimated_completion = models.DateField(null=True, blank=True)
    budget_allocated = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Response for {self.incident.title}"

# Citizen Comments on Incidents
class IncidentComment(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='comments')
    citizen = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)  # Verified citizen comment
    
    def __str__(self):
        return f"Comment by {self.citizen.username}"

# AI Model for Incident Classification
class AIModelVersion(models.Model):
    model_name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    description = models.TextField()
    accuracy = models.FloatField()
    trained_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.model_name} v{self.version}"

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

class IncidentReport(models.Model):
    URGENCY_CHOICES = [
        ('pending', 'Pending AI Review'),
        ('urgent', 'Urgent'),
        ('not_urgent', 'Not Urgent'),
        ('manual_review', 'Needs Manual Review'),
    ]
    
    # FIXED: Use settings.AUTH_USER_MODEL
    citizen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300)
    category = models.CharField(max_length=100)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='pending')
    ai_confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.urgency}"
    
    def analyze_urgency(self):
        """Analyze report urgency using AI"""
        try:
            from ai_model.inference.classifier import ReportClassifier
            
            classifier = ReportClassifier()
            result = classifier.predict(self.description)
            
            # Update fields based on AI prediction
            if result['is_urgent']:
                self.urgency = 'urgent'
            else:
                self.urgency = 'not_urgent'
                
            self.ai_confidence = result['confidence']
            
            # If confidence is low, flag for manual review
            if result['confidence_level'] == 'medium':
                self.urgency = 'manual_review'
            
            self.save()
            return result
        except Exception as e:
            # Fallback if AI fails
            print(f"AI analysis failed: {e}")
            self.urgency = 'manual_review'
            self.save()
            return {'error': str(e)}