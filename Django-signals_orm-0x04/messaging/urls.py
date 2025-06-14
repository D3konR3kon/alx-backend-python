from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    ConversationViewSet, 
    MessageViewSet, 
    UserRegistrationView, 
    UserProfileView, 
    UserListView, 
    UserDetailView, 
    mark_conversation_as_read, 
    mark_message_as_read,
    notification_list,
    notification_count_api,
    mark_notification_read,
    mark_all_notifications_read,
    mark_conversation_notifications_read,
    unread_messages_inbox,
    unread_count
)

# API routers
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'users', UserListView, basename='users')

# Nested router for conversation messages
conversations_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

app_name = 'chats'

urlpatterns = [
    # Core resource endpoints
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),

    # Authentication
    path('auth/register/', UserRegistrationView.as_view(), name='auth-register'),
    path('auth/profile/', UserProfileView.as_view(), name='auth-profile'),
    
    # User details
    path('users/<uuid:user_id>/', UserDetailView.as_view(), name='user-detail'),

    # Notifications
    path('notifications/', notification_list, name='notifications-list'),
    path('notifications/count/', notification_count_api, name='notifications-count'),
    path('notifications/<uuid:notification_id>/read/', mark_notification_read, name='notification-read'),
    path('notifications/mark-all-read/', mark_all_notifications_read, name='notifications-mark-all'),
    path('notifications/conversations/<uuid:conversation_id>/mark-read/', 
         mark_conversation_notifications_read, 
         name='notifications-conversation-read'),

    # Message read tracking
    path('messages/unread/', unread_messages_inbox, name='messages-unread'),
    path('messages/unread/count/', unread_count, name='messages-unread-count'),
    path('messages/<uuid:message_id>/mark-read/', mark_message_as_read, name='message-read'),
    path('conversations/<uuid:conversation_id>/mark-read/', mark_conversation_as_read, name='conversation-read'),
]