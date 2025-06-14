from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message, Notification, ConversationParticipant

User = get_user_model()

@receiver(post_save, sender=Message)
def create_message_notifications(sender, instance, created, **kwargs):
    """
    Notifications for all conversation participants when a new message is sent or created
    """
    if not created or instance.message_type == 'system': 
        return
    
    participants = ConversationParticipant.objects.filter(
        conversation=instance.conversation,
        is_active=True
    ).exclude(user=instance.sender)
    
    notifications_to_create = []
    
    for participant in participants:
        if participant.is_muted:
            continue
            
        if instance.conversation.conversation_type == 'group':
            title = f"New message in {instance.conversation.title or 'Group Chat'}"
        else:
            title = f"New message from {instance.sender.get_full_name() or instance.sender.username}"

        if instance.message_type == 'text':
            message_preview = instance.message_body[:100] + "..." if len(instance.message_body) > 100 else instance.message_body
        else:
            message_preview = f"Sent a {instance.get_message_type_display().lower()}"
        
        notification = Notification(
            recipient=participant.user,
            sender=instance.sender,
            notification_type='new_message',
            title=title,
            message=message_preview,
            related_message=instance,
            related_conversation=instance.conversation
        )
        notifications_to_create.append(notification)
    
    if notifications_to_create:
        Notification.objects.bulk_create(notifications_to_create)


@receiver(post_save, sender=Message)
def handle_message_mentions(sender, instance, created, **kwargs):
    """
    Special notifications for mentioned users in messages
    """
    if not created or instance.message_type != 'text':
        return
    
    words = instance.message_body.split()
    mentions = []
    
    for word in words:
        if word.startswith('@') and len(word) > 1:
            username = word[1:].strip('.,!?;:')
            try:
                mentioned_user = User.objects.get(username=username)
                if mentioned_user != instance.sender:
                    mentions.append(mentioned_user)
            except User.DoesNotExist:
                continue
    
    mention_notifications = []
    for mentioned_user in mentions:
        is_participant = ConversationParticipant.objects.filter(
            conversation=instance.conversation,
            user=mentioned_user,
            is_active=True
        ).exists()
        
        if is_participant:
            notification = Notification(
                recipient=mentioned_user,
                sender=instance.sender,
                notification_type='mention',
                title=f"You were mentioned by {instance.sender.get_full_name() or instance.sender.username}",
                message=f"In: {instance.message_body[:100]}...",
                related_message=instance,
                related_conversation=instance.conversation
            )
            mention_notifications.append(notification)
    
    if mention_notifications:
        Notification.objects.bulk_create(mention_notifications)