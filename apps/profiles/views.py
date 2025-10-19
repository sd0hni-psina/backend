from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Profile
from .serializers import UserPublicSerializer, ProfileSerializer

User = get_user_model()

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        return Profile.objects.select_related('user').all()
    
    @action(detail=False, methods=['get'], url_path='me')
    def my_profile(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'], url_path='me')
    def update_my_profile(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        try:
            profile = queryset.get(pk=pk)
        except (ValueError, Profile.DoesNotExist):
            profile = get_object_or_404(queryset, user__username=pk)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)