from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer

class ChatViewSet(viewsets.ModelViewSet):

    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(participants=user).prefetch_related('participants', 'messages')
    
    @action(detail=True, methods=['post'], url_path='messages')
    def get_messages(self, request, pk=None):
        
        chat = self.get_object()
        messages = chat.messages.order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='send')
    def send_message(self, request, pk=None):

        chat = self.get_object()
        user = request.user
        text = request.data.get('text', '').strip()

        if not text:
            return Response({'detail': 'Text fields cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        message = Message.objects.create(chat=chat, sender=user, text=text)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='start')
    def start_chat(self, request):

        user = request.user
        target_id = request.data.get('user_id')

        if not target_id:
            return Response({'detail': 'Net 2 uchastnika'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            target = Chat._meta.get_field('participants').related_model.objects.get(id=target_id)
        except:
            return Response({'detail': 'User  not found'}, status=status.HTTP_404_NOT_FOUND)
        
        existing = Chat.objects.filter(participants=user).filter(participants=target).first()
        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        chat = Chat.objects.create()
        chat.participants.add(user, target)
        serializer = self.get_serializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):

        chat = self.get_object()
        user = request.user

        updated = chat.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)
        self.request._request
        group_name = f'chat_{chat.id}'

        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'chat.read',
                'chat_id': chat.id,
                'reader_id': user.id,
            }
        )

        return Response({'detail': f'Mark {updated} messages as'}, status=status.HTTP_200_OK)   