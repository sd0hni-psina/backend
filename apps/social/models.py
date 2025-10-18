from django.db import models
from django.conf import settings

class FriendRequest(models.Model):
    """Model dlya zaprosov v druzya"""

    STATUS_CHOICES = (
        ('pending', 'В ожидании'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Ссылаемся на кастомную модель пользователя
        on_delete = models.CASCADE, # при удалении пользователя удалить все его запросы
        related_name= 'sent_friend_requests', # получить все запросы, которые этот пользователь отправил.
        verbose_name='Отправитель',
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.CASCADE,
        related_name='received_requests',
        verbose_name='Получатель',
    )
    status = models.CharField(
        max_length = 10,
        choices = STATUS_CHOICES,
        default = 'pending',
        verbose_name='Статус',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Запрос в друзья'
        verbose_name_plural = 'Запросы в друзья'
        unique_together = ('sender', 'receiver')
        indexes = [
            models.Index(fields=['sender', 'status']),
            models.Index(fields=['receiver', 'status']),
        ] # Фильтрация по статусу отправителя и получателя 
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if self.sender == self.receiver:
            raise ValueError("Нельзя отправить запрос самому себе.")
        super().save(*args, **kwargs)
    
    def accept(self):
        """Принять запрос в друзья"""
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()
            
            # Создаем взаимную дружбу
            Friendship.objects.get_or_create(
                user=self.receiver,
                friend=self.sender
            )
            Friendship.objects.get_or_create(
                user=self.sender,
                friend=self.receiver
            )
            return True
        return False
    
    def rejected(self):
        """Отклонить запрос в друзья"""
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()
            return True
        return False 

    def __str__(self):
        return f'Запрос от {self.sender} к {self.receiver}'
    
class Friendship(models.Model):
    """Model dlya druzey"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'friendships',
        verbose_name='Пользователь',
    )
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'friends',
        verbose_name='Друг',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Дружба'
        verbose_name_plural = 'Друзья'
        unique_together = ('user', 'friend')
        constraints = [
            models.CheckConstraint(
                check = models.Q(user__lt = models.F('friend')) | models.Q(user__isnull = True) | models.Q(friend__isnull=True),
                name = 'friendship_order'
            )
        ]
    
    # @staticmethod
    # def make_friends(user1, user2):
    #     if user1.id > user2.id:
    #         user1, user2 = user2, user1
    #     return Friendship.objects.get_or_create(user=user1, friend=user2)
    
    def __str__(self):
        return f'{self.user} и {self.friend} - друзья'

class Follow(models.Model):
    """model dlya podpischikov"""

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'following',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'followers',
        verbose_name='Подписка на',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
        ]
    
    def save(self, *args, **kwargs):
        if self.follower == self.following:
            raise ValueError("Нельзя подписаться на самого себя.")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.follower} подписан на {self.following}'