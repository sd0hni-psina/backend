from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ChatManager(models.Manager):
    """Custom manager для работы с чатами"""
    
    def get_or_create_dm(self, user1, user2):
        """Получить или создать Direct Message между двумя пользователями"""
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        # Поиск существующего чата
        chats = self.all().prefetch_related('participants')
        for chat in chats:
            participants = set(chat.participants.values_list('id', flat=True))
            if participants == {user1.id, user2.id}:
                return chat, False
        
        # Создание нового
        chat = self.create()
        chat.participants.add(user1, user2)
        return chat, True


class Chat(models.Model):
    """Chat между двумя пользователями (Direct Message)"""

    participants = models.ManyToManyField(
        User,
        related_name='chats',
        verbose_name='Участники'
    )
    last_message = models.ForeignKey(
        'Message',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='Последнее сообщение'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,  # ✅ индекс для сортировки
        verbose_name='Дата создания'
    )
    
    objects = ChatManager()  # ✅ custom manager
    
    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'
        indexes = [  # ✅ индекс для быстрого получения чатов
            models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        usernames = ', '.join([u.username for u in self.participants.all()[:2]])
        return f'Chat ({usernames})'
    
    def unread_count_for_user(self, user) -> int:
        """Количество непрочитанных сообщений для пользователя"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """Сообщение в чате"""

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages',  # ✅ важно для serializer'а
        verbose_name='Чат'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Отправитель'
    )
    text = models.TextField(
        max_length=2000,
        verbose_name='Текст'
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,  # ✅ индекс для фильтра непрочитанных
        verbose_name='Прочитано'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    is_edited = models.BooleanField(
        default=False,
        verbose_name='Отредактировано'
    )
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']
        indexes = [  # ✅ индексы для производительности
            models.Index(fields=['chat', 'is_read']),
            models.Index(fields=['sender', '-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """✅ Валидация: sender должен быть в participants"""
        if not self.chat.participants.filter(pk=self.sender.id).exists():
            raise ValueError(f"{self.sender} не является участником чата {self.chat.id}")
        super().save(*args, **kwargs)
    
    def mark_as_read(self) -> None:
        """✅ Отметить сообщение как прочитанное"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
    
    @classmethod
    def mark_chat_as_read(cls, chat, user) -> int:
        """✅ Отметить все сообщения в чате как прочитанные для пользователя"""
        return cls.objects.filter(
            chat=chat,
            is_read=False
        ).exclude(sender=user).update(is_read=True)
    
    def edit(self, new_text: str) -> None:
        """✅ Отредактировать сообщение"""
        if self.text != new_text:
            self.text = new_text
            self.is_edited = True
            self.save(update_fields=['text', 'is_edited', 'updated_at'])
    
    def can_delete(self, user) -> bool:
        """✅ Может ли пользователь удалить это сообщение"""
        return self.sender == user
    
    def __str__(self):
        return f'Message from {self.sender.username} in chat {self.chat.id}'