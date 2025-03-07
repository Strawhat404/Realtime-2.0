import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import BeaconDevice, ProximityEvent, Notification
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class BeaconConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        # Ensure a real User instance for unauthenticated case
        if not self.user.is_authenticated:
            # Use an existing user or create a test user
            self.user = await database_sync_to_async(User.objects.get_or_create)(
                username='testuser', defaults={'password': 'testpass'}
            )[0]
        self.room_name = f"user_{(self.user.id if self.user.id else 'anonymous')}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        logger.info(f"Connected to group: {self.room_name}")

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)
            logger.info(f"Disconnected from group: {self.room_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            event_type = data.get('type')
            logger.info(f"Received: {data}")
            if event_type == 'proximity_event':
                await self.handle_proximity_event(data)
            elif event_type == 'notification_ack':
                await self.handle_notification_ack(data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Invalid JSON format'}))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        notification = Notification.objects.get(id=notification_id, user=self.user)
        notification.is_read = True
        notification.save()

    @database_sync_to_async
    def create_proximity_event(self, beacon_id, distance):
        beacon = BeaconDevice.objects.get(id=beacon_id)
        return ProximityEvent.objects.create(
            beacon=beacon,
            user=self.user,  # Now a real User instance
            distance=distance
        )

    async def handle_notification_ack(self, data):
        try:
            notification_id = data['notification_id']
            await self.mark_notification_read(notification_id)
            await self.send(text_data=json.dumps({'status': 'Notification acknowledged'}))
        except Notification.DoesNotExist:
            await self.send(text_data=json.dumps({'error': 'Notification not found'}))
        except Exception as e:
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def handle_proximity_event(self, data):
        try:
            event = await self.create_proximity_event(
                data['beacon_id'],
                data['distance']
            )
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'proximity_update',
                    'beacon_id': data['beacon_id'],
                    'distance': data['distance'],
                    'timestamp': event.timestamp.isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Proximity event error: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def proximity_update(self, event):
        await self.send(text_data=json.dumps(event))