from django.contrib import admin


# chats/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Conversation, ConversationParticipant, Message, MessageReaction


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
    list_display = ('id', 'title', 'conversation_type', 'created_by', 'created_at', 'is_active')
    list_filter = ('conversation_type', 'is_active', 'created_at')
    search_fields = ('title', 'created_by__email')
    inlines = [ConversationParticipantInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'conversation', 'message_type', 'content_preview', 'created_at', 'is_deleted')
    list_filter = ('message_type', 'is_edited', 'is_deleted', 'created_at')
    search_fields = ('content', 'sender__email')
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        if obj.message_type == 'text' and obj.content:
            return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
        return f"[{obj.message_type}]"
    content_preview.short_description = 'Content Preview'


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__email', 'message__content')