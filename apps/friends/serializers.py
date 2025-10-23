from rest_framework import serializers
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from .models import FriendRequest, Friendship, Follow
from django.contrib.auth import get_user_model

User = get_user_model()

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault)
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.fields['receiver'].queryset = get_user_model().objects.all()
    
    def validate(self, attrs):
        sender = self.context['request'].user
        receiver = attrs.get('receiver')

        if sender == receiver:
            raise serializers.ValidationError('u cant request yourself')
        if Friendship.objects.filter(
            Q(user1=sender, user2=receiver) | Q(user1=receiver, user2=sender)
        ).exists():
            raise serializers.ValidationError('Youre friends')
        
        existing_request = FriendRequest.objects.filter(
            Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender),
            status=FriendRequest.STATUS_PENDING
        ).exists()
        if existing_request:
            raise serializers.ValidationError('Request proccessed')
        
        return attrs
    
    def create(self, validated_data):
        sender = validated_data['sender']
        receiver = validated_data['receiver']

        friend_request = FriendRequest.objects.create(**validated_data)

        Follow.objects.get_or_create(follower=sender, following=receiver)

        return friend_request

class FriendshipSerializer(serializers.ModelSerializer):
    user1 = serializers.SerializerMethodField()
    user2 = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ['id', 'user1', 'user2', 'created_at']

    def get_user1(self, obj):
        return str(obj.user1)
    
    def get_user2(self,obj):
        return str(obj.user2)
    
class FolloweSerializer(serializers.ModelSerializer):
    follower = serializers.StringRelatedField()
    following = serializers.StringRelatedField()

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']