from django.db import models
from django.conf import settings
from django.db.models import Q, F
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class FriendRequset(models.Model):
    """Models for request to friend"""

    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friend_request_sent',
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friend_request_receiver'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,  # потому что часто будут фильтрации по status
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False, 
    )
    
    class Meta:
        constraints = [ # не даёт создать два одинаковых запроса от одного отправителя к одному получателю
            models.UniqueConstraint(fields=['sender', 'receiver'],name='unique_friendrequest'),
        ]
        indexes = [ # ускорит получение входящих pending запросов
            models.Index(fields=['receiver', 'status']),
        ]
        ordering = ['-created_at']
    
    def accept(self):
        if self.status == self.STATUS_ACCEPTED:
            return None, False
        self.status = self.STATUS_ACCEPTED
        self.save(update_fields='status')
        return self, True
    
    def rejected(self):
        if self.status == self.STATUS_REJECTED:
            return None, False
        self.status = self.STATUS_REJECTED
        self.save(update_fields='status')
        return self, True
    
    def cancel(self):
        if self.pk:
            self.delete()
            return True
        return False
    
    def __str__(self):
        return f"FriendRequest(from{self.sender}, to={self.receiver}, status={self.status})"

class Friendship(models.Model):
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friendship_initiated',
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friendship_received'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_friendship_pair'),
            models.CheckConstraint(check=~Q(user1=F('user2')), name='no_self_friendship'),
        ]
        indexes = [
            models.Index(fields=['user1', 'user2']),
        ]
    
    def save(self,*args, **kwargs):
        if self.user1_id and self.user2_id:
            if self.user1_id == self.user2_id:
                raise ValueError('You cant')
            if self.user1_id > self.user2_id:
                self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Friendship({self.user1}<->{self.user2})"

class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_relations',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower_relations',
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'following'], name='unique_follow'),
            models.CheckConstraint(check=~Q(follower=F('following')), name='no_self_follow'),
        ]
        indexes = [
            models.Index(fields=['following', 'follower']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Follow({self.follower}->{self.following})"