
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CustomerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add('customer_group', self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('customer_group', self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Broadcast the received message to the group
        await self.channel_layer.group_send(
            'customer_group',
            {
                'type': 'customer.message',
                'message': message,
                'username': self.scope['user'].username,
            }
        )

    async def customer_message(self, event):
        message = event['message']
        username = event['username']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))