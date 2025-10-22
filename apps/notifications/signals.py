from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.posts.models import Like, Comment
from apps.friends.models import FriendRequest
from .utils import create_notification


@receiver(post_save, sender=Like)
def notify_like(sender, instance, created, **kwargs):
    if created:
        recipient = instance.post.author
        sender_user = instance.user
        if recipient != sender_user:
            create_notification(recipient=recipient, sender=sender_user, type='like', content_object=instance.post)


@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    if created:
        recipient = instance.post.author
        sender_user = instance.user
        if recipient != sender_user:
            create_notification(sender=sender_user, recipient=recipient, type='comment', content_object=instance.post)


@receiver(post_save, sender=FriendRequest)
def notify_friend_request(sender, instance, created, **kwargs):
    if created:
        create_notification(recipient=instance.receiver, sender=instance.sender, type='friend_request', content_object=instance)
    elif instance.status == 'accepted':
        create_notification(recipient=instance.sender, sender=instance.receiver, type='friend_accept', content_object=instance)

