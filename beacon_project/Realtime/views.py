from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import BeaconDevice, ProximityEvent, Notification
from .serializers import BeaconDeviceSerializer, ProximityEventSerializer, NotificationSerializer

class BeaconDeviceViewSet(viewsets.ModelViewSet):
    queryset = BeaconDevice.objects.all()
    serializer_class = BeaconDeviceSerializer

    @action(detail=True, methods=['GET'])
    def events(self, request, pk=None):
        beacon = self.get_object()
        events = ProximityEvent.objects.filter(beacon=beacon)
        serializer = ProximityEventSerializer(events, many=True)
        return Response(serializer.data)

class ProximityEventViewSet(viewsets.ModelViewSet):
    serializer_class = ProximityEventSerializer

    def get_queryset(self):
        return ProximityEvent.objects.filter(user=self.request.user)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def unread(self, request):
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)