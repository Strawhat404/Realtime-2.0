import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ProximityEvent, Notification, BeaconDevice

class BeaconConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            event_type = data.get('type')
            
            if event_type == 'proximity_event':
                await self.handle_proximity_event(data)
            elif event_type == 'notification_ack':
                await self.handle_notification_ack(data)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))

    @database_sync_to_async
    def create_proximity_event(self, beacon_id, distance):
        beacon = BeaconDevice.objects.get(id=beacon_id)
        return ProximityEvent.objects.create(
            beacon=beacon,
            user=self.user,
            distance=distance
        )

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
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    async def proximity_update(self, event):
        await self.send(text_data=json.dumps(event))