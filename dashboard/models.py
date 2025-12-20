from django.db import models
from core.models import User
from incidents.models import Incident

# Dashboard Statistics
class CityStatistics(models.Model):
    city = models.CharField(max_length=100, unique=True)
    total_incidents = models.IntegerField(default=0)
    resolved_incidents = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0)  # in hours
    citizen_satisfaction = models.FloatField(default=0)  # 0-100%
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Stats: {self.city}"

# Heatmap Data
class HeatmapData(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    intensity = models.FloatField()  # Number of incidents in area
    incident_type = models.CharField(max_length=100)
    date = models.DateField()
    
    class Meta:
        unique_together = ['latitude', 'longitude', 'date', 'incident_type']

# Institutional Report
class InstitutionalReport(models.Model):
    institution = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    period_start = models.DateField()
    period_end = models.DateField()
    report_data = models.JSONField()  # All statistics in JSON format
    generated_at = models.DateTimeField(auto_now_add=True)
    pdf_report = models.FileField(upload_to='reports/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.institution.username}"