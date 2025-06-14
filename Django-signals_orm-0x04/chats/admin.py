# chats/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Notification, User, Conversation, ConversationParticipant, Message, MessageReaction


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin"""
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_online', 'last_seen', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_online', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'profile_picture', 'bio', 'is_online', 'last_seen')
        }),
    )


class ConversationParticipantInline(admin.TabularInline):
    model = ConversationParticipant
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('conversation_id', 'title', 'conversation_type', 'created_by', 'created_at', 'is_active')
    list_filter = ('conversation_type', 'is_active', 'created_at')
    search_fields = ('title', 'created_by__email')
    inlines = [ConversationParticipantInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'sender', 'conversation', 'message_type', 'content_preview', 'sent_at', 'is_deleted')
    list_filter = ('message_type', 'is_edited', 'is_deleted', 'sent_at')
    search_fields = ('message_body', 'sender__email')
    readonly_fields = ('sent_at', 'updated_at')
    
    def content_preview(self, obj):
        if obj.message_type == 'text' and obj.message_body:
            return obj.message_body[:50] + "..." if len(obj.message_body) > 50 else obj.message_body
        return f"[{obj.message_type}]"
    content_preview.short_description = 'Content Preview'


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__email', 'message__content')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_id', 'recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username', 'sender__username')
    ordering = ('-created_at',)