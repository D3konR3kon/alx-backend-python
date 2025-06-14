

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import ( ConversationViewSet, 
    MessageViewSet, 
    UserRegistrationView, 
    UserProfileView, 
    UserListView, 
    UserDetailView,
    notification_list,
    notification_count_api,
    mark_notification_read,
    mark_all_notifications_read,
    mark_conversation_notifications_read
)


router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='messages')

conversations_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),

    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
    path('users/<uuid:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('nots/', notification_list, name='list'),
    path('count/', notification_count_api, name='count_api'),
    path('<uuid:notification_id>/read/', mark_notification_read, name='mark_read'),
    path('mark-all-read/', mark_all_notifications_read, name='mark_all_read'),
    path('conversation/<uuid:conversation_id>/mark-read/', 
         mark_conversation_notifications_read, 
         name='mark_conversation_read'),
]
