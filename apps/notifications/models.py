from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ("friend_request", "Запрос в друзья"),
        ("friend_accept", "Принятие дружбы"),
        ("like", "Лайк"),
        ("comment", "Комментарий"),
        ("follow", "Подписка"),
        ("message", 'Новое сообщение')
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='sent_notifications',
        null=True,
        blank=True,
    )

    type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', '-created_at']),
        ]

    def __str__(self):
        return f'{self.sender} -> {self.recipient} ({self.type})'
