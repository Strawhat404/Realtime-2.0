import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from .models import BeaconDevice, ProximityEvent
from beacon_project.asgi import application

@pytest.mark.asyncio
async def test_websocket_connection():
    communicator = WebsocketCommunicator(application, "ws/beacon/")
    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()

@pytest.mark.django_db
def test_beacon_device_creation():
    beacon = BeaconDevice.objects.create(
        uuid="550e8400-e29b-41d4-a716-446655440000",
        name="Test Beacon",
        location="Test Location"
    )
    assert beacon.name == "Test Beacon"
    assert beacon.is_active == True