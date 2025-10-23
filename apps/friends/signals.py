from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import FriendRequest, Friendship, Follow

@receiver(post_save, sender=FriendRequest)
def handle_friend_request_accept(sender, instance, created, **kwargs):
    if created:
        return
    if instance.status == FriendRequest.STATUS_ACCEPTED:
        with transaction.atomic():
            Friendship.objects.get_or_create(user1=instance.sender, user2=instance.receiver)
            Follow.objects.filter(follower=instance.sender, following=instance.receiver).delete()
            Follow.objects.filter(follower=instance.receiver, following=instance.sender).delete()

    elif instance.status == FriendRequest.STATUS_REJECTED:
        Follow.objects.filter(follower=instance.sender, following=instance.receiver).delete()
    
@receiver(post_delete, sender=FriendRequest)
def handle_friendship_delete(sender, instance, **kwargs):
    with transaction.atomic():
        Follow.objects.filter(follower=instance.user1, following=instance.user2).delete()
        Follow.objects.filter(follower=instance.user2, following=instance.user1).delete()
