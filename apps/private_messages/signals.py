from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from apps.notifications.utils import create_notification

@receiver(post_save, sender=Message)
def notify_on_message(sender, instance, created, **kwargs):
    if not created:
        return
    chat = instance.chat
    sender_user = instance.sender
   
    recipients = chat.participants.exclude(id=sender_user.id)
    for recipient in recipients:
        create_notification(recipient=recipient, sender=sender_user, type="message", content_object=instance)
