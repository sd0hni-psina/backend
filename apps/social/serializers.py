from rest_framework import serializers
from .models import FriendRequest, Friendship, Follow
from apps.users.models import User

class UserMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'last_name', 'first_name', 'email')

class FriendRequestSerializer(serializers.ModelSerializer):
    """dlya otpravki i polucheniya zaprosov v druzya"""
    sender = UserMinSerializer(read_only=True)
    receiver = UserMinSerializer(read_only=True)
    receiver_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FriendRequest
        fields = (
            'id', 'sender', 
            'receiver', 'receiver_id',
            'status', 'created_at', 'updated_at')
        read_only_fields = ('status', 'created_at', 'updated_at')

    def create(self, validated_data):
        sender = self.context['request'].user
        receiver_id = validated_data.pop('receiver_id')

        if sender.id == receiver_id:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")
        
        if FriendRequest.objects.filter(
            sender_id=sender.id,
            receiver_id=receiver_id
        ).exists():
            raise serializers.ValidationError("Friend request already sent.")
        
        return FriendRequest.objects.create(
            sender=sender, 
            receiver_id=receiver_id, 
            **validated_data
        )
    
class FriendshipSerializer(serializers.ModelSerializer):
    """dlya otobrazheniya druzey"""
    user = UserMinSerializer(read_only=True)
    friend = UserMinSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ('id', 'friend', 'created_at', 'user')
        read_only_fields = ('created_at',)

class FollowSerializer(serializers.ModelSerializer):
    """dlya otobroazheniya podpischikov"""

    follower = UserMinSerializer(read_only=True)
    following = UserMinSerializer(read_only=True)
    following_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Follow
        fields = ('id', 'follower', 'following', 'following_id', 'created_at')
        read_only_fields = ('created_at',)
    
    def create(self, validated_data):
        follower = self.context['request'].user
        following_id = validated_data.pop('following_id')

        if follower.id == following_id:
            raise serializers.ValidationError("You cannot follow yourself.")
        
        if not User.objects.filter(id=following_id).exists():
            raise serializers.ValidationError("User not found.")
        
        if Follow.objects.filter(
            follower=follower,
            following_id=following_id
        ).exists():
            raise serializers.ValidationError("You are already following this user.")
        
        return Follow.objects.create(
            follower=follower,
            following_id=following_id,
            **validated_data
        )

class AcceptFriendRequestSerializer(serializers.Serializer):
    """prinyat zapros v druz`ya"""
    
    def validate(self, attrs):
        request = self.context.get('request')
        friend_request = self.context.get('friend_request')

        if not friend_request:
            raise serializers.ValidationError('Запрос не найден')
        if friend_request.receiver !=request.user:
            raise serializers.ValidationError('Вы не можете принять запрос')
        if friend_request.status != 'pending':
            raise serializers.ValidationError('Запро с обработке')
        
        return attrs
    
    def save(self):
        friend_request = self.context.get('friend_requset')
        user = friend_request.receiver
        friend = friend_request.sender

        friend_request.status = 'accepted'
        friend_request.save()

        Friendship.objects.get_or_create(user=user,friend=friend)
        Friendship.objects.get_or_create(user=friend, friend=user)

        return friend_request

class RejectFriendRequestSerializer(serializers.Serializer):
    """otklonit` zapros v druz`ya"""

    def validate(self,attrs):
        friend_request = self.instance

        if friend_request.status != 'pending':
            raise serializers.ValidationError('You can only reject pending friend requests.')
        
        if friend_request.receiver != self.context['request'].user:
            raise serializers.ValidationError('You are not authorized to reject this friend request.')
        
        return attrs
    
    def save(self):
        self.instance.rejected()
        return self.instance
    
class UnfollowSerializer(serializers.Serializer):
    """otpiska ot polzovatelya"""

    def validate(self, attrs):
        follow = self.instance

        if follow.follower != self.context['request'].user:
            raise serializers.ValidationError('You can only unfollow users you follow.')
        
        return attrs
    
    def save(self):
        self.instance.delete()
        return None
    
class RemoveFriendSerializer(serializers.Serializer):
    """udalit` iz druzey"""

    def validate(self, attrs):
        friendship = self.instance

        if friendship.user != self.context['request'].user:
            raise serializers.ValidationError('You can only remove friends you added.')
        
        return attrs
    
    def save(self):
        self.instance.delete()
        return None
