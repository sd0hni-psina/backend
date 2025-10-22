from rest_framework.routers import DefaultRouter
from django.urls import path, include

from apps.posts.views import PostViewSet
from apps.friends.views import FriendRequestViewSet, FriendshipViewSet, FollowViewSet
from apps.profiles.views import ProfileViewSet
from apps.notifications.views import NotificationViewSet

router = DefaultRouter()

router.register(r'posts', PostViewSet, basename='post')
router.register(r'request', FriendRequestViewSet, basename='friend-requests')
router.register(r'friends', FriendshipViewSet, basename='friends')
router.register(r'follow', FollowViewSet, basename='follow')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),

    path('users/', include('apps.users.urls')),
]
