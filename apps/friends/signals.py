from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import FriendRequset, Friendship, Follow

@receiver(post_save, sender=FriendRequset)
def handle_friend_request_accept(sender, instance, created, **kwargs):
    if created:
        return
    if instance.status == FriendRequset.STATUS_ACCEPTED:
        with transaction.atomic():
            Friendship.objects.get_or_create(user1=instance.sender, user2=instance.receiver)
            Follow.objects.filter(follower=instance.sender, following=instance.receiver).delete()
            Follow.objects.filter(follower=instance.receiver, following=sender).delete()

    elif instance.status == FriendRequset.STATUS_REJECTED:
        Follow.objects.filter(follower=instance.sender, following=instance.receiver).delete()
    
@receiver(post_delete, sender=FriendRequset)
def handle_friendship_delete(sender, instance, **kwargs):
    with transaction.atomic():
        Follow.objects.get_or_create(follower=instance.user1, following=instance.user2)
