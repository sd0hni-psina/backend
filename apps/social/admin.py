from django.contrib import admin
from django.utils.html import format_html
from .models import FriendRequset, Friendship, Follow


@admin.register(FriendRequset)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status_badge', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('sender__username', 'receiver__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Участники', {
            'fields': ('sender', 'receiver')
        }),
        ('Статус', {
            'fields': ('status',)
        }),
        ('Дата и время', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ('accept_requests', 'reject_requests')
    
    def status_badge(self, obj):
        """Отображение статуса с цветными бэджами"""
        colors = {
            'pending': '#FFA500',    # Оранжевый
            'accepted': '#00AA00',   # Зелёный
            'rejected': '#FF0000',   # Красный
        }
        labels = {
            'pending': 'В ожидании',
            'accepted': 'Принят',
            'rejected': 'Отклонен',
        }
        color = colors.get(obj.status, '#808080')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            label
        )
    status_badge.short_description = 'Статус'
    
    def accept_requests(self, request, queryset):
        """Быстрое действие для принятия запросов"""
        count = 0
        for friend_request in queryset.filter(status='pending'):
            friend_request.accepted()
            count += 1
        self.message_user(request, f'Принято {count} запросов в друзья.')
    accept_requests.short_description = 'Принять выбранные запросы'
    
    def reject_requests(self, request, queryset):
        """Быстрое действие для отклонения запросов"""
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'Отклонено {count} запросов в друзья.')
    reject_requests.short_description = 'Отклонить выбранные запросы'


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'created_at', 'friendship_duration')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'friend__username')
    readonly_fields = ('created_at', 'friendship_duration')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Друзья', {
            'fields': ('user', 'friend')
        }),
        ('Информация', {
            'fields': ('created_at', 'friendship_duration'),
            'classes': ('collapse',)
        }),
    )
    
    def friendship_duration(self, obj):
        """Показывает как долго люди дружат"""
        from django.utils import timezone
        duration = timezone.now() - obj.created_at
        days = duration.days
        if days == 0:
            return 'Менее суток'
        elif days == 1:
            return '1 день'
        else:
            return f'{days} дней'
    friendship_duration.short_description = 'Продолжительность дружбы'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at', 'follow_status')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Подписка', {
            'fields': ('follower', 'following')
        }),
        ('Дата создания', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ('unfollow_users',)
    
    def follow_status(self, obj):
        """Визуальный статус подписки"""
        return format_html(
            '<span style="background-color: #0066CC; color: white; padding: 3px 10px; border-radius: 3px;">Активна</span>'
        )
    follow_status.short_description = 'Статус'
    
    def unfollow_users(self, request, queryset):
        """Быстрое действие для отписки"""
        count = queryset.delete()[0]
        self.message_user(request, f'{count} подписок удалено.')
    unfollow_users.short_description = 'Удалить выбранные подписки'