from django.contrib import admin
from .models import (
    IncidentCategory, Incident, IncidentUpdate, 
    InstitutionResponse, IncidentComment, AIModelVersion
)

@admin.register(IncidentCategory)
class IncidentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority_level', 'response_time_hours')
    search_fields = ('name', 'description')

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'citizen', 'city', 'urgency', 'status', 'created_at')
    list_filter = ('status', 'urgency', 'city', 'created_at')
    search_fields = ('title', 'description', 'address')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(IncidentUpdate)
admin.site.register(InstitutionResponse)
admin.site.register(IncidentComment)
admin.site.register(AIModelVersion)