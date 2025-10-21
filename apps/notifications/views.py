from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user,).select_related('sender', 'recipient')
    
    @action(detail=True, methods=['patch'], url_path='read')
    def mark_as_read(self, request, pk=None):
        """Otmetit kak prochitannoe"""
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({'detail': 'Notification was read'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['patch'], url_path='read-all')
    def mark_all_as_read(self, request):
        """Otmetit vse uvedomleniya kak prochtenye"""
        updated = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'detail': f'Noted {updated} notifications'}, status=status.HTTP_200_OK)
    
