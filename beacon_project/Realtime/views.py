from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import BeaconDevice, ProximityEvent, Notification
from .serializers import BeaconDeviceSerializer, ProximityEventSerializer, NotificationSerializer

class BeaconDeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage BeaconX Pro W6 devices.
    - GET: List all beacons or retrieve a specific beacon.
    - POST: Create a new beacon.
    - PUT/PATCH: Update beacon details.
    - DELETE: Remove a beacon.
    """
    queryset = BeaconDevice.objects.all()
    serializer_class = BeaconDeviceSerializer

    @swagger_auto_schema(
        method='get',
        operation_description="Retrieve all proximity events for a specific beacon.",
        responses={200: ProximityEventSerializer(many=True)}
    )
    @action(detail=True, methods=['GET'])
    def events(self, request, pk=None):
        beacon = self.get_object()
        events = ProximityEvent.objects.filter(beacon=beacon)
        serializer = ProximityEventSerializer(events, many=True)
        return Response(serializer.data)

class ProximityEventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for proximity events between users and beacons.
    - GET: List events for the authenticated user.
    - POST: Record a new proximity event.
    """
    serializer_class = ProximityEventSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return ProximityEvent.objects.filter(user=user)
        return ProximityEvent.objects.none()  # Return empty queryset for anon users

class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user notifications triggered by beacon interactions.
    - GET: List notifications for the authenticated user.
    - POST: Create a new notification.
    """
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Notification.objects.filter(user=user)
        return Notification.objects.none()  # Return empty queryset for anon users

    @swagger_auto_schema(
        method='get',
        operation_description="Retrieve unread notifications for the authenticated user.",
        responses={200: NotificationSerializer(many=True)}
    )
    @action(detail=False, methods=['GET'])
    def unread(self, request):
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)