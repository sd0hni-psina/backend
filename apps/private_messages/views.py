from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatViewSet(viewsets.ModelViewSet):
    """ViewSet для управления чатами"""
    
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(
            participants=user
        ).prefetch_related('participants', 'messages').order_by('-created_at')
    
    @action(detail=True, methods=['get'], url_path='messages')
    def get_messages(self, request, pk=None):
        """✅ Получить сообщения чата с pagination"""
        chat = self.get_object()
        messages = chat.messages.order_by('-created_at')
        
        # ✅ Pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='send')
    def send_message(self, request, pk=None):
        """Отправить сообщение в чат"""
        chat = self.get_object()
        user = request.user
        text = request.data.get('text', '').strip()

        if not text:
            return Response(
                {'detail': 'Text cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ Валидация: пользователь в чате?
        if not chat.participants.filter(id=user.id).exists():
            return Response(
                {'detail': 'You are not a participant of this chat'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message = Message.objects.create(chat=chat, sender=user, text=text)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='start')
    def start_chat(self, request):
        """Начать или получить существующий DM"""
        user = request.user
        target_id = request.data.get('user_id')

        if not target_id:
            return Response(
                {'detail': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ Правильный поиск пользователя
        try:
            target = User.objects.get(id=target_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user == target:
            return Response(
                {'detail': 'Cannot start chat with yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ Использовать custom manager
        chat, created = Chat.objects.get_or_create_dm(user, target)
        serializer = self.get_serializer(chat)
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Отметить все сообщения в чате как прочитанные"""
        chat = self.get_object()
        user = request.user
        
        # ✅ Используем метод модели
        updated = Message.mark_chat_as_read(chat, user)
        
        # Отправить в WebSocket об обновлении
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{chat.id}',
            {
                'type': 'chat.read',  # ✅ правильный тип
                'chat_id': chat.id,
                'reader_id': user.id,
            }
        )
        
        return Response(
            {'detail': f'Marked {updated} messages as read'},
            status=status.HTTP_200_OK
        )