import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from core.models import LeaveRequest, Employee, CompanyAdmin
from django.utils import timezone

class LeaveRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'leave_requests'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'join_company':
                company_id = data.get('company_id')
                if company_id:
                    # Join company-specific room
                    company_room = f'leave_requests_company_{company_id}'
                    await self.channel_layer.group_add(
                        company_room,
                        self.channel_name
                    )
                    self.company_room = company_room
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON data'
            }))

    # Receive message from room group
    async def leave_request_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'leave_request_update',
            'action': event['action'],
            'data': event['data']
        }))
