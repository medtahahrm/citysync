from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import IncidentReport

@receiver(post_save, sender=IncidentReport)
def analyze_report_on_save(sender, instance, created, **kwargs):
    """Automatically analyze report when created"""
    if created and instance.urgency == 'pending':
        # Run AI analysis in background (use Celery for production)
        instance.analyze_urgency()