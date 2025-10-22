from django.contrib import admin
from .models import Chat, Message

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', '-created_at']
    filter_horizontal = ['participants']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['chat', 'sender', 'short_text', 'is_read', 'created_at']

    def short_text(self, obj):
        return obj.text[:30] + ('...' if len(obj.text) > 30 else '')
    
