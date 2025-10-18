from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from .models import FriendRequest, Friendship, Follow
from django.db import models
from .serializers import (
    FriendRequestSerializer,
    FriendshipSerializer,
    FollowSerializer,
    AcceptFriendRequestSerializer,
    RejectFriendRequestSerializer,
    UnfollowSerializer,
    RemoveFriendSerializer,
)

class FriendRequestViewSet(viewsets.ModelViewSet):
    """sozdnaie i prosmotr spiska zaprosov v druz`ya"""

    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        #фильтр который показывает пользователю 
        #только те запросы, где он отправитель или получатель.
        return FriendRequest.objects.filter( 
            models.Q(sender=self.request.user) |models.Q(receiver=self.request.user)
        )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Prinyat` drujbu"""
        friend_request = self.get_object()
        serializer = AcceptFriendRequestSerializer(
            friend_request,
            data=request.data,
            context={'request': request, 'friend_request': friend_request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Otklonit drujbu"""
        friend_request = self.get_object()
        serializer = RejectFriendRequestSerializer(
            friend_request,
            data=request.data,
            context={'request': request, 'friend_request': friend_request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

class FriendshipViewSet(viewsets.ModelViewSet):
    """dlya upravleniya druzyami"""

    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Friendship.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def remove(self, request, pk=None):
        """Udalit iz druzei"""
        friendship = self.get_object()
        serializer = RemoveFriendSerializer(
            data=request.data,
            context={'request': request, 'friendship': friendship}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FollowViewSet(viewsets.ModelViewSet):
    """dlya upravleniem podpischikami"""
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        action = self.action
        if action == 'followers':
            return Follow.objects.filter(following=self.request.user).select_related('follower')
        elif action == 'following':
            return Follow.objects.filter(follower=self.request.user).select_related('following')
        return Follow.objects.filter(follower=self.request.user).select_related('following')
    
    @action(detail=False, methods=['get'])
    def followers(self, request):
        """spisok podpischikov"""
        return self.list(request)
    @action(detail=False, methods=['get'])
    def following(self, request):
        """spisok podisok"""
        return self.list(request)
    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        """Otpisatsya"""
        follow = self.get_object()
        serializer = UnfollowSerializer(
            data=request.data,
            context={'request': request, 'follow': follow}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)