from django import forms
from .models import Incident, IncidentCategory

class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            'title', 'description', 'category', 
            'address', 'city', 'neighborhood',
            'image', 'video', 'audio_note',
            'is_anonymous'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields not required for initial report
        self.fields['category'].required = False
        self.fields['image'].required = False
        self.fields['city'].initial = 'Casablanca'  # Default city

class IncidentUpdateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['status', 'urgency']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'urgency': forms.Select(attrs={'class': 'form-control'}),
        }