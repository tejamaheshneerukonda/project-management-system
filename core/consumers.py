import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage, ChatNotification, Employee

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send room info
        room_info = await self.get_room_info()
        await self.send(text_data=json.dumps({
            'type': 'room_info',
            'room': room_info
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(text_data_json)
        elif message_type == 'typing':
            await self.handle_typing(text_data_json)
        elif message_type == 'stop_typing':
            await self.handle_stop_typing(text_data_json)

    async def handle_chat_message(self, data):
        content = data.get('content', '').strip()
        if not content:
            return
            
        # Get user and employee
        user = self.scope['user']
        if not user.is_authenticated:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Authentication required'
            }))
            return
            
        employee = await self.get_employee(user)
        if not employee:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Employee profile not found'
            }))
            return
            
        # Create message
        message = await self.create_message(employee, content)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'sender_name': f"{employee.first_name} {employee.last_name}",
                    'sender_id': employee.id,
                    'content': message.content,
                    'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_edited': message.is_edited,
                }
            }
        )
        
        # Create notifications for offline users
        await self.create_notifications(employee, message)

    async def handle_typing(self, data):
        user = self.scope['user']
        if not user.is_authenticated:
            return
            
        employee = await self.get_employee(user)
        if not employee:
            return
            
        # Send typing indicator to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing',
                'user': f"{employee.first_name} {employee.last_name}",
                'user_id': employee.id
            }
        )

    async def handle_stop_typing(self, data):
        user = self.scope['user']
        if not user.is_authenticated:
            return
            
        employee = await self.get_employee(user)
        if not employee:
            return
            
        # Send stop typing indicator to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'stop_typing',
                'user_id': employee.id
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))

    # Receive typing indicator from room group
    async def typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
            'user_id': event['user_id']
        }))

    # Receive stop typing indicator from room group
    async def stop_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'stop_typing',
            'user_id': event['user_id']
        }))

    @database_sync_to_async
    def get_employee(self, user):
        try:
            return user.employee_profile
        except:
            return None

    @database_sync_to_async
    def get_room_info(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return {
                'id': room.id,
                'name': room.name,
                'room_type': room.room_type,
                'participants_count': room.participants.count()
            }
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message(self, employee, content):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            message = ChatMessage.objects.create(
                room=room,
                sender=employee,
                content=content,
                message_type='TEXT'
            )
            return message
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def create_notifications(self, sender, message):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            participants = room.participants.exclude(id=sender.id)
            
            for participant in participants:
                ChatNotification.objects.create(
                    recipient=participant,
                    sender=sender,
                    room=room,
                    message=message,
                    notification_type='NEW_MESSAGE',
                    title=f'New message in {room.name}',
                    content=f'{sender.first_name}: {message.content[:100]}...'
                )
        except ChatRoom.DoesNotExist:
            pass