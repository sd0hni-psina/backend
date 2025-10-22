import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Chat, Message
from apps.notifications.utils import create_notification

User = get_user_model()

class ChatConsumers(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_id = int(self.scope['url_route']['kwargs']['chat_id'])
        self.group_name = f'chat_{self.chat_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        is_participant = await database_sync_to_async(self.check_participant)()
        if not is_participant:
            await self.close(code=4003)
            return
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def receive(self, text_data = None, bytes_data = None):
        
        if text_data is None:
            return
        data = json.load(text_data)
        action = data.get('action')

        if action == 'send_message':
            text = data.get('text', '').strip()
            if not text:
                await self.send_json({'error': 'empty_text'})
                return
            
            message = await database_sync_to_async(self.create_message)(self.user, text)

            recipient = await database_sync_to_async(self.get_other_participant)(self.user)
            if recipient:
                await database_sync_to_async(create_notification)(
                    recipient=recipient,
                    sender=self.user,
                    type='message',
                    content_object=message,
                )
            
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'chat': self.chat_id,
                        'text': message.text,
                        'sender': {'id': self.user.id, 'username': self.user.username},
                        'created_at': message.created_at.isoformat(),
                        'is_read': message.is_read,
                    },
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dump({'event': 'new_message', 'data': event['message']}))
    
    async def check_participants(self):
        try:
            chat = Chat.objects.get(id=self.chat_id)
        except Chat.DoesNotExist:
            return False
        return chat.participants.filter(id=self.user.id).exists()
    
    def create_message(self, user, text):
        chat = Chat.objects.get(id=self.chat_id)
        message = Message.objects.create(chat=chat, sender=user, text=text)
        return message
    
    def get_other_participants(self, user):

        chat = Chat.objects.get(id=self.chat_id)
        participants = list(chat.participants.exclude(id=user.id))
        return participants[0] if participants else None
    
    async def send_json(self, obj):
        await self.send(text_data=json.dumps(obj))
    
    async def chat_read(self, event):
        await self.send_json({
            'event': 'messages_read',
            'data': {'chat_id': event['chat_id'], 'reader_id': event['reader_id']}
        })
