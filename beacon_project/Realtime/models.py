from django.db import models
from django.conf import settings
# from django.contrib.gis.db import models as gis_models

class BeaconDevice(models.Model):
    uuid = models.UUIDField(unique=True)
    name = models.CharField(max_length=100)
    # location = gis_models.PointField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.uuid}"

class ProximityEvent(models.Model):
    beacon = models.ForeignKey(BeaconDevice, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    distance = models.FloatField()  # in meters
    timestamp = models.DateTimeField(auto_now_add=True)
    motion_detected = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']

class Notification(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    beacon = models.ForeignKey(BeaconDevice, on_delete=models.CASCADE)
    message = models.TextField()
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='MEDIUM')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']