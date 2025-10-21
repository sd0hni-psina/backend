from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()



class SenderSerializer(serializers.ModelSerializer):
    """Korotokoe predstavlenie otpravitelya uvedimleniya"""
    class Meta:
        models = User
        fields = ['id', 'username']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer dlay uvedomleniya"""
    sender = SenderSerializer(read_only=True)
    recipient = SenderSerializer(read_only=True)
    content_object_str = serializers.SerializerMethodField()

    class Meta:
        models = Notification
        fields = ['id', 'type', 'sender', 'recipient', 'content_object_str', 'is_read', 'created_at']

    def get_content_object_str(self, obj):
        if obj.content_object:
            return str(obj.content_object)
        return None