from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Post, Like, Comment
from .serializers import PostSerializer, LikeSerializer, CommentSerializer
from apps.friends.models import Friendship, Follow
from django.db.models import Q, F, When, Case, Value


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Tolko avtor mojet redaktirovat ili udalyat` posty"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class PostViewSet(viewsets.ModelViewSet):

    serializer_class = PostSerializer
    queryset = Post.objects.select_related('author').all()
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_queryset(self):
        queryset = Post.objects.select_related('author').all()
        author_username = self.request.query_params.get("author")

        if author_username:
            queryset = queryset.filter(author__username=author_username)
        return queryset
    
    @action(detail=False, methods=['get'], url_path='my')
    def my_posts(self, request):
        posts = Post.objects.filter(author=request.user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["post"], url_path="like")
    def like(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            return Response({"detail": "Лайк удалён."}, status=status.HTTP_200_OK)
        return Response({"detail": "Пост лайкнут."}, status=status.HTTP_201_CREATED)

    # ---------- КОММЕНТАРИИ ----------
    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)

        if request.method == "GET":
            comments = post.comments.select_related("user")
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        elif request.method == "POST":
            serializer = CommentSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    @action(detail=False, methods=['get'], url_path='feed')
    def feed(self, request):
        user = request.user

        friend_ids = Friendship.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).values_list('user1_id', 'user2_id')

        friends_set = {uid for pair in friend_ids
                       for uid in pair if uid != user.id}
        
        following_ids = set(
            Follow.objects.filter(follower=user).values_list('following_id', flat=True)
        )

        visible_authors = friends_set | following_ids | {user.id}

        posts = Post.objects.filter(
            author_id__in=visible_authors,
            is_public=True
        ).select_related('author').order_by('-created_at')

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

        # flat_firends_ids = set()
        # for pair in friend_ids:
        #     flat_firends_ids.update(pair)
        # flat_firends_ids.discard(user.id)

        # following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
        # visible_authors = set(flat_firends_ids) | set(following_ids) | {user.id}

        # posts = (
        #     Post.objects.filter(author_id__in=visible_authors).select_related('author').order_by('-created_at')
        # )

        # serializer = self.get_serializer(posts, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)