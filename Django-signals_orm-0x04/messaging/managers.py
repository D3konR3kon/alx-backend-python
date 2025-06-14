from django.db import models

class UnreadMessagesManager(models.Manager):
    """
    Custom manager to filter unread messages for a specific user
    """
    def for_user(self, user):
        """
        Get all unread messages for a specific user across all conversations
        they participate in
        """
        return self.get_queryset().filter(
            conversation__conversation_participants__user=user,
            conversation__conversation_participants__is_active=True,
            is_read=False,
            is_deleted=False
        ).exclude(sender=user).select_related('sender', 'conversation').distinct()
    
    def for_user_optimized(self, user):
        """
        Get unread messages with only necessary fields for performance
        """
        return self.for_user(user).only(
            'message_id',
            'message_body',
            'message_type',
            'sent_at',
            'sender__username',
            'sender__email',
            'conversation__conversation_id',
            'conversation__title',
            'conversation__conversation_type'
        )
    
    def count_for_user(self, user):
        """
        Get count of unread messages for a user
        """
        return self.for_user(user).count()
