from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Message, Chat
from apps.notifications.utils import create_notification


@receiver(post_save, sender=Message)
def update_chat_last_message(sender, instance, created, **kwargs):
    """✅ Обновить последнее сообщение в чате"""
    if created:
        instance.chat.last_message = instance
        instance.chat.save(update_fields=['last_message'])


@receiver(post_delete, sender=Message)
def update_chat_last_message_on_delete(sender, instance, **kwargs):
    """✅ При удалении сообщения обновить last_message на предыдущее"""
    chat = instance.chat
    last_msg = chat.messages.first()  # первое из-за ordering = ['-created_at']
    if last_msg:
        chat.last_message = last_msg
    else:
        chat.last_message = None
    chat.save(update_fields=['last_message'])