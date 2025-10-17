from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('friend-request', views.FriendRequestViewSet, basename='friend-request')
router.register('friends', views.FriendshipViewSet, basename='friendsip')
router.register('follows', views.FollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
]
