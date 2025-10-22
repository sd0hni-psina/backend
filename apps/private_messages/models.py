from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Chat(models.Model):
    """Chat mejdu dvumya polzovatelyami"""

    participants = models.ManyToManyField(
        User,
        related_name='chats',
    )
    created_at = models.DateTimeField(default=timezone.now)
     
    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        usernames = ', '.join([u.username for u in self.participants.all()])
        return f'Chat ({usernames})'

class Message(models.Model):
    """Sami soobweniya vnutri chata"""

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
    )
    text = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
    
    def __str__(self):
        return f'Сообщениe ot {self.sender.username} in chat {self.chat.id}'