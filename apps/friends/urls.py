from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import FriendRequestViewSet, FriendshipViewSet, FollowViewSet

router = DefaultRouter()

router.register(r'request', FriendRequestViewSet, basename='friend-requests')

router.register(r'', FriendshipViewSet, basename='friends')

router.register(r'follow', FollowViewSet, basename='followe')

urlpatterns = [
    path('', include(router.urls)),
]
