from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Chat, Message

User = get_user_model()


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']
    
class MessageSerializer(serializers.ModelSerializer):
    sender = UserShortSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'text', 'is_read', 'created_ad']
        read_only_fields = ['id', 'sender', 'is_read', 'created_at', 'chat']

class ChatSerializer(serializers.ModelSerializer):
    participants = UserShortSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'last_message', 'created_at']

    def get_last_message(self, obj):
        last = obj.message.order_by('-created_at').first()
        if last:
            return MessageSerializer(last).data
        return None 