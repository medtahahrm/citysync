from django.contrib import admin
from .models import CityStatistics, HeatmapData, InstitutionalReport

admin.site.register(CityStatistics)
admin.site.register(HeatmapData)
admin.site.register(InstitutionalReport)