from django.contrib import admin
from .models import Chat, Message


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_participants', 'created_at']  # ✅ правильный display
    filter_horizontal = ['participants']
    readonly_fields = ['created_at']
    
    def get_participants(self, obj):
        """✅ Отобразить участников"""
        return ', '.join([u.username for u in obj.participants.all()])
    get_participants.short_description = 'Участники'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['chat', 'sender', 'short_text', 'is_read', 'is_edited', 'created_at']
    list_filter = ['is_read', 'is_edited', 'created_at']
    search_fields = ['sender__username', 'text']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Информация', {'fields': ('chat', 'sender', 'text')}),
        ('Статус', {'fields': ('is_read', 'is_edited')}),
        ('Дата', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def short_text(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    short_text.short_description = 'Текст'