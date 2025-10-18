from django.contrib import admin
from .models import FriendRequset, Friendship, Follow


@admin.register(FriendRequset)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("sender__username", "receiver__username")
    ordering = ("-created_at",)
    autocomplete_fields = ("sender", "receiver")

    fieldsets = (
        (None, {"fields": ("sender", "receiver", "status")}),
        ("Дополнительно", {"fields": ("created_at",)}),
    )
    readonly_fields = ("created_at",)

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ("id", "user1", "user2", "created_at")
    search_fields = ("user1__username", "user2__username")
    ordering = ("-created_at",)
    autocomplete_fields = ("user1", "user2")
    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {"fields": ("user1", "user2")}),
        ("Дополнительно", {"fields": ("created_at",)}),
    )

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    autocomplete_fields = ("follower", "following")
    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {"fields": ("follower", "following")}),
        ("Дополнительно", {"fields": ("created_at",)}),
    )