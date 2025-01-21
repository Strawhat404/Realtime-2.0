from rest_framework import serializers
from .models import BeaconDevice, ProximityEvent, Notification

class BeaconDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeaconDevice
        fields = '__all__'

class ProximityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProximityEvent
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'