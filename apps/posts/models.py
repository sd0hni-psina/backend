from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    text = models.TextField(
        max_length=2000,
    )
    image = models.ImageField(
        upload_to='posts/',
        null=True,
        blank=True,
    )
    is_public = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']

    def __str__(self):
        return f'Прост {self.id} от {self.author.username}'
    
    @property
    def short_text(self):
        return self.text[:100] + ('...' if len(self.text) > 100 else '')
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    def comments_count(self):
        return self.comments.count()
    
class Like(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'post') # не позволит лайкнуть один и тот же пост дважды
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'

    def __str__(self):
        return f'{self.user.username} liked {self.post.id}'
    
class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Comment {self.user.username} to post {self.post.id}'
    
