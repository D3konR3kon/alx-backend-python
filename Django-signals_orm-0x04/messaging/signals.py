from datetime import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from messaging.utils.thread_local import get_current_user
from .models import Message, Notification, ConversationParticipant, MessageHistory

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

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        original = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    if original.message_body != instance.message_body:
        MessageHistory.objects.create(
            message=original,
            previous_body=original.message_body,
            edited_by=get_current_user()
        )
        instance.is_edited = True
        instance.edited_at = timezone.now()
        instance.edited_by = get_current_user()