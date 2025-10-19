from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.conf import settings
from .models import FriendRequest, Friendship, Follow
from .serializers import FriendRequestSerializer, FriendshipSerializer, FolloweSerializer


class FriendRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(Q(sender=user) | Q(receiver=user))
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='incoming')
    def incoming_request(self, request):
        qs = FriendRequest.objects.filter(receiver=request.user, status=FriendRequest.STATUS_PENDING)
        serializer =self.get_serializer(qs, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'], url_path='outgoing')
    def outgoing_requests(self, request):
        qs = FriendRequest.objects.filter(sender=request.user, status=FriendRequest.STATUS_PENDING)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        friend_request = self.get_object()
        if friend_request.receiver != request.user:
            return Response({"detail": "Kakaya ta ne nuzhanoe uslovie, kak po mne"})
        friend_request.accept()
        return Response({"detail": "Successfully"}, status=status.HTTP_200_OK)
    @action(detail=True, methods=['delete'], url_path='cancel')
    def cancel(self, request, pk=None):
        friend_request = self.get_object()
        if friend_request.sender != request.user:
            return Response({"detail": "Ewe odin ne nujnyi"})
        friend_request.cancel()
        return Response({"detail": "Canceled"}, status=status.HTTP_204_NO_CONTENT)

class FriendshipViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        qs = Friendship.objects.filter(Q(user1=user) | Q(user2=user))
        serializer = FriendshipSerializer(qs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'], url_path='remove')
    def remove_friend(self, request, pk=None):
        friend = get_object_or_404(settings.AUTH_USER_MODEL, pk=pk)
        Friendship.objects.filter(
            Q(user1=request.user, user2=friend) | Q(user1=friend, user2=request.user)
        ).delete()
        return Response({"detail": "Freind was removed"}, status=status.HTTP_204_NO_CONTENT)
    
class FollowViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='followers')
    def followers(self, requset):
        qs = Follow.objects.filter(following=requset.user)
        serializer = FolloweSerializer(qs, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'], url_path='following')
    def following(self, request):
        qs = Follow.objects.filter(follower=request.user)
        serializer = FolloweSerializer(qs, many=True)
        return Response(serializer.data)
    @action(detail=True, methods=['delete'], url_path='unfollow')
    def unfollow(self, request, pk=None):
        user_to_unfollow = get_object_or_404(settings.AUTH_USER_MODEL, pk=pk)
        Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
        return Response({"detail": "Unfollow successfully"}, status=status.HTTP_204_NO_CONTENT)
    