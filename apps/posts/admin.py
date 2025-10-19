from django.contrib import admin
from .models import Post, Like, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'short_text', 'is_public', 'created_at']
    search_fields = ['text', 'author__username']
    list_filter = ['is_public', 'created_at']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    search_fields = ['user__name', 'post__text']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'short_text', 'created_at']
    search_fields = ['user__username', 'post__text']

    def short_text(self, obj):
        return obj.text[:20] + ('...' if len(obj.text) > 20 else '') 