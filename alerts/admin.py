from django.contrib import admin
from .models import AlertType, Alert, AlertSubscription, UserAlertReceipt

admin.site.register(AlertType)
admin.site.register(Alert)
admin.site.register(AlertSubscription)
admin.site.register(UserAlertReceipt)