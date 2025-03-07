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
        if not self.user.is_authenticated:
            logger.warning(f"Unauthorized connection attempt from {self.scope.get('client', 'unknown')}")
            await self.close(code=4001)
            return
        self.room_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        logger.info(f"User {self.user.username} connected to group: {self.room_name}")

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)
            logger.info(f"User {self.user.username} disconnected from group: {self.room_name} with code {close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            event_type = data.get('type')
            logger.info(f"Received from {self.user.username}: {data}")
            if event_type == 'proximity_event':
                await self.handle_proximity_event(data)
            elif event_type == 'notification_ack':
                await self.handle_notification_ack(data)
            else:
                await self.send(text_data=json.dumps({'error': 'Unknown event type'}))
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
            user=self.user,
            distance=distance
        )

    async def handle_notification_ack(self, data):
        try:
            notification_id = data.get('notification_id')
            if not notification_id:
                raise ValueError("Missing notification_id")
            await self.mark_notification_read(notification_id)
            await self.send(text_data=json.dumps({'status': 'Notification acknowledged'}))
        except Notification.DoesNotExist:
            await self.send(text_data=json.dumps({'error': 'Notification not found'}))
        except Exception as e:
            logger.error(f"Notification ack error for {self.user.username}: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def handle_proximity_event(self, data):
        try:
            beacon_id = data.get('beacon_id')
            distance = data.get('distance')
            if beacon_id is None or distance is None:
                raise ValueError("Missing beacon_id or distance")
            event = await self.create_proximity_event(beacon_id, distance)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'proximity_update',
                    'beacon_id': beacon_id,
                    'distance': distance,
                    'timestamp': event.timestamp.isoformat()
                }
            )
        except BeaconDevice.DoesNotExist:
            await self.send(text_data=json.dumps({'error': 'BeaconDevice not found'}))
        except Exception as e:
            logger.error(f"Proximity event error for {self.user.username}: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def proximity_update(self, event):
        await self.send(text_data=json.dumps(event))