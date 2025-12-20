from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Alert, AlertType

class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = [
            'alert_type', 'title', 'description', 'severity',
            'affected_areas', 'latitude', 'longitude', 'radius_km',
            'valid_until', 'source', 'instructions', 'emergency_numbers'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'affected_areas': forms.Textarea(attrs={'rows': 3}),
            'instructions': forms.Textarea(attrs={'rows': 4}),
            'emergency_numbers': forms.Textarea(attrs={'rows': 2}),
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default valid_until to 24 hours from now
        if not self.instance.pk:
            default_time = timezone.now() + timedelta(hours=24)
            self.fields['valid_until'].initial = default_time.strftime('%Y-%m-%dT%H:%M')
        
        # Make location fields optional
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['radius_km'].required = False