
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
import uuid


class User(AbstractUser):
    """
    Extended User model with additional fields for messaging functionality
    """
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.get_full_name() or self.username})"
    
    def update_last_seen(self):
        """Update the user's last seen timestamp"""
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])


class Conversation(models.Model):
    """
    Model to track conversations between users
    """
    CONVERSATION_TYPES = [
        ('direct', 'Direct Message'),
        ('group', 'Group Chat'),
    ]
    
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, null=True)  # For group chats
    conversation_type = models.CharField(max_length=10, choices=CONVERSATION_TYPES, default='direct')
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ConversationParticipant',
        related_name='conversations'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'conversations'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.conversation_type == 'group' and self.title:
            return f"Group: {self.title}"
        else:
            participants = self.participants.all()[:2]
            if len(participants) >= 2:
                return f"Chat: {participants[0].username} & {participants[1].username}"
            return f"Conversation {self.conversation_id}"
    
    def get_last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.first()
    
    def get_unread_count(self, user):
        """Get unread message count for a specific user"""
        try:
            participant = self.conversation_participants.get(user=user)
            return self.messages.filter(
                sent_at__gt=participant.last_read_at
            ).exclude(sender=user).count()
        except ConversationParticipant.DoesNotExist:
            return 0


class ConversationParticipant(models.Model):
    """
    Through model to track user participation in conversations
    """
    PARTICIPANT_ROLES = [
        ('member', 'Member'),
        ('admin', 'Admin'),
        ('owner', 'Owner'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='conversation_participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_conversations'
    )
    role = models.CharField(max_length=10, choices=PARTICIPANT_ROLES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(default=timezone.now)
    is_muted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'conversation_participants'
        unique_together = ['conversation', 'user']
        verbose_name = 'Conversation Participant'
        verbose_name_plural = 'Conversation Participants'
    
    def __str__(self):
        return f"{self.user.username} in {self.conversation}"
    
    def mark_as_read(self):
        """Mark all messages as read up to now"""
        self.last_read_at = timezone.now()
        self.save(update_fields=['last_read_at'])


class Message(models.Model):
    """
    Model for individual messages within conversations
    """
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('system', 'System Message'),
    ]
    
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    message_body = models.TextField(blank=True)  # Text content - renamed from 'content'
    file_attachment = models.FileField(upload_to='message_files/', blank=True, null=True)
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)  # Renamed from 'created_at'
    updated_at = models.DateTimeField(auto_now=True)
    
    # Message reactions
    reactions = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='MessageReaction',
        related_name='reacted_messages'
    )
    
    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-sent_at']  # Updated to use 'sent_at'
    
    def __str__(self):
        if self.message_type == 'text':
            preview = self.message_body[:50] + "..." if len(self.message_body) > 50 else self.message_body
            return f"{self.sender.username}: {preview}"
        else:
            return f"{self.sender.username}: [{self.message_type}]"
    
    def mark_as_edited(self):
        """Mark message as edited"""
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save(update_fields=['is_edited', 'edited_at'])
    
    def soft_delete(self):
        """Soft delete the message"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])


class MessageReaction(models.Model):
    """
    Model for message reactions (emoji responses)
    """
    REACTION_TYPES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😂'),
        ('angry', '😠'),
        ('sad', '😢'),
        ('wow', '😮'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='message_reactions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_reactions'
    )
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_reactions'
        unique_together = ['message', 'user', 'reaction_type']
        verbose_name = 'Message Reaction'
        verbose_name_plural = 'Message Reactions'
    
    def __str__(self):
        return f"{self.user.username} reacted {self.get_reaction_type_display()} to message {self.message.message_id}"


class Notification(models.Model):
    """
    Model to store user notifications
    """
    NOTIFICATION_TYPES = [
        ('new_message', 'New Message'),
        ('mention', 'Mention'),
        ('reaction', 'Message Reaction'),
        ('conversation_invite', 'Conversation Invite'),
        ('system', 'System Notification'),
    ]
    
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    related_message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_conversation = models.ForeignKey(
        'Conversation',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_sent(self):
        """Mark notification as sent (for external notifications)"""
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save(update_fields=['is_sent', 'sent_at'])   