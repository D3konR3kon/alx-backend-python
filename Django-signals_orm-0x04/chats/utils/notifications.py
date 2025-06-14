from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import Notification, ConversationParticipant

User = get_user_model()


class NotificationManager:
    """
    Utility class for managing notifications
    """
    
    @staticmethod
    def get_unread_notifications(user):
        """Get all unread notifications for a user"""
        return Notification.objects.filter(
            recipient=user,
            is_read=False
        ).select_related('sender', 'related_conversation').order_by('-created_at')
    
    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for a user"""
        return Notification.objects.filter(
            recipient=user,
            is_read=False
        ).count()
    
    @staticmethod
    def mark_conversation_notifications_read(user, conversation):
        """Mark all notifications from a specific conversation as read"""
        notifications = Notification.objects.filter(
            recipient=user,
            related_conversation=conversation,
            is_read=False
        )
        
        current_time = timezone.now()
        notifications.update(
            is_read=True,
            read_at=current_time
        )
        
        return notifications.count()
    
    @staticmethod
    def mark_all_notifications_read(user):
        """Mark all notifications for a user as read"""
        notifications = Notification.objects.filter(
            recipient=user,
            is_read=False
        )
        
        current_time = timezone.now()
        count = notifications.update(
            is_read=True,
            read_at=current_time
        )
        
        return count
    
    @staticmethod
    def create_custom_notification(recipient, title, message, notification_type='system', sender=None, related_message=None, related_conversation=None):
        """Create a custom notification"""
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            related_message=related_message,
            related_conversation=related_conversation
        )
        return notification
    
    @staticmethod
    def cleanup_old_notifications(days=30):
        """Clean up old read notifications"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        deleted_count = Notification.objects.filter(
            is_read=True,
            read_at__lt=cutoff_date
        ).delete()[0]
        
        return deleted_count


def get_notification_context(notification):
    """
    Get additional context for a notification for display purposes
    """
    context = {
        'notification': notification,
        'time_ago': timezone.now() - notification.created_at,
        'sender_name': notification.sender.get_full_name() or notification.sender.username if notification.sender else 'System',
        'conversation_name': None,
        'message_preview': notification.message
    }
    
    if notification.related_conversation:
        if notification.related_conversation.conversation_type == 'group':
            context['conversation_name'] = notification.related_conversation.title or 'Group Chat'
        else:
            participants = notification.related_conversation.participants.exclude(
                user_id=notification.recipient.user_id
            )[:1]
            if participants:
                context['conversation_name'] = participants[0].get_full_name() or participants[0].username
    
    return context