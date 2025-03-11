from django.contrib import admin
from .models import BeaconDevice, ProximityEvent, Notification  # Import your models

# Register your models
admin.site.register(BeaconDevice)
admin.site.register(ProximityEvent)
admin.site.register(Notification)