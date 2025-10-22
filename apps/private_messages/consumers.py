import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Chat, Message
from apps.notifications.utils import create_notification

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket Consumer для real-time чатов"""

    async def connect(self):
        self.chat_id = int(self.scope['url_route']['kwargs']['chat_id'])
        self.group_name = f'chat_{self.chat_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        # Проверить что пользователь участник чата
        is_participant = await self.check_participant()
        if not is_participant:
            await self.close(code=4003)
            return
        
        # Добавить в группу
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        """Отключиться от группы"""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def receive(self, text_data=None, bytes_data=None):
        """Получить сообщение от клиента"""
        if text_data is None:
            return
        
        try:
            data = json.loads(text_data)  # ✅ json.loads() вместо json.load()
        except json.JSONDecodeError:
            await self.send_json({'error': 'invalid_json'})
            return
        
        action = data.get('action')

        if action == 'send_message':
            text = data.get('text', '').strip()
            if not text:
                await self.send_json({'error': 'empty_text'})
                return
            
            message = await self.create_message(text)
            
            # Отправить уведомление получателю
            recipient = await self.get_other_participant()
            if recipient:
                await database_sync_to_async(create_notification)(
                    recipient=recipient,
                    sender=self.user,
                    type='message',
                    content_object=message,
                )
            
            # Отправить всем в группе
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat.message',  # ✅ chat.message вместо chat_message
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
        """Отправить сообщение клиенту"""
        await self.send_json({
            'event': 'new_message',
            'data': event['message']
        })
    
    async def chat_read(self, event):
        """Отправить событие прочтения"""
        await self.send_json({
            'event': 'messages_read',
            'data': {'chat_id': event['chat_id'], 'reader_id': event['reader_id']}
        })
    
    async def check_participant(self):
        """✅ Правильно: async метод с database_sync_to_async"""
        try:
            chat = await database_sync_to_async(Chat.objects.get)(id=self.chat_id)
            return await database_sync_to_async(
                lambda: chat.participants.filter(id=self.user.id).exists()
            )()
        except Chat.DoesNotExist:
            return False
    
    async def create_message(self, text):
        """✅ Правильно: async обёртка БД операции"""
        def _create():
            chat = Chat.objects.get(id=self.chat_id)
            return Message.objects.create(chat=chat, sender=self.user, text=text)
        
        return await database_sync_to_async(_create)()
    
    async def get_other_participant(self):
        """✅ Правильно: async метод"""
        def _get():
            chat = Chat.objects.get(id=self.chat_id)
            participants = list(chat.participants.exclude(id=self.user.id))
            return participants[0] if participants else None
        
        return await database_sync_to_async(_get)()
    
    async def send_json(self, obj):
        """Отправить JSON"""
        await self.send(text_data=json.dumps(obj))  # ✅ json.dumps() вместо json.dump()