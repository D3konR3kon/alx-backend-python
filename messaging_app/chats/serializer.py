# chats/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import User, Conversation, ConversationParticipant, Message, MessageReaction

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Basic User serializer for general user information
    """
    full_name = serializers.SerializerMethodField()
    is_online_status = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'phone_number', 'profile_picture', 'bio', 
            'is_online', 'is_online_status', 'last_seen', 'created_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'last_seen']
    
    def get_full_name(self, obj):
        """Get user's full name or fallback to username"""
        full_name = obj.get_full_name()
        return full_name if full_name.strip() else obj.username
    
    def get_is_online_status(self, obj):
        """Determine if user is currently online based on last_seen"""
        if obj.is_online:
            return "online"
        
        # Consider user online if last seen within 5 minutes
        time_threshold = timezone.now() - timezone.timedelta(minutes=5)
        if obj.last_seen and obj.last_seen > time_threshold:
            return "recently_active"
        
        return "offline"


class UserProfileSerializer(UserSerializer):
    """
    Extended User serializer for profile management (includes sensitive fields)
    """
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['updated_at']
        read_only_fields = UserSerializer.Meta.read_only_fields + ['updated_at']


class UserMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal User serializer for nested relationships (reduces payload size)
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['user_id', 'username', 'first_name', 'last_name', 'full_name', 'profile_picture', 'is_online']
        read_only_fields = ['user_id']
    
    def get_full_name(self, obj):
        full_name = obj.get_full_name()
        return full_name if full_name.strip() else obj.username


class MessageReactionSerializer(serializers.ModelSerializer):
    """
    Serializer for message reactions
    """
    user = UserMinimalSerializer(read_only=True)
    reaction_emoji = serializers.SerializerMethodField()
    
    class Meta:
        model = MessageReaction
        fields = ['id', 'user', 'reaction_type', 'reaction_emoji', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_reaction_emoji(self, obj):
        """Get the emoji representation of the reaction"""
        return dict(MessageReaction.REACTION_TYPES).get(obj.reaction_type, '')


class MessageSerializer(serializers.ModelSerializer):
    """
    Main Message serializer with nested relationships
    """
    sender = UserMinimalSerializer(read_only=True)
    reply_to_message = serializers.SerializerMethodField()
    reactions = MessageReactionSerializer(source='message_reactions', many=True, read_only=True)
    reaction_summary = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    is_own_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'message_type', 'message_body', 
            'file_attachment', 'file_url', 'reply_to', 'reply_to_message',
            'is_edited', 'edited_at', 'is_deleted', 'sent_at', 'updated_at',
            'reactions', 'reaction_summary', 'replies_count', 'is_own_message'
        ]
        read_only_fields = [
            'message_id', 'sent_at', 'updated_at', 'is_edited', 
            'edited_at', 'is_deleted'
        ]
    
    def get_reply_to_message(self, obj):
        """Get basic info about the message being replied to"""
        if obj.reply_to and not obj.reply_to.is_deleted:
            return {
                'message_id': obj.reply_to.message_id,
                'sender': UserMinimalSerializer(obj.reply_to.sender).data,
                'message_type': obj.reply_to.message_type,
                'message_body': obj.reply_to.message_body[:100] + "..." if len(obj.reply_to.message_body) > 100 else obj.reply_to.message_body,
                'sent_at': obj.reply_to.sent_at
            }
        return None
    
    def get_reaction_summary(self, obj):
        """Get a summary of reactions (count by type)"""
        reactions = obj.message_reactions.all()
        summary = {}
        for reaction in reactions:
            reaction_type = reaction.reaction_type
            if reaction_type not in summary:
                summary[reaction_type] = {
                    'count': 0,
                    'emoji': dict(MessageReaction.REACTION_TYPES).get(reaction_type, ''),
                    'users': []
                }
            summary[reaction_type]['count'] += 1
            summary[reaction_type]['users'].append(reaction.user.username)
        return summary
    
    def get_replies_count(self, obj):
        """Get count of replies to this message"""
        return obj.replies.filter(is_deleted=False).count()
    
    def get_file_url(self, obj):
        """Get the full URL for file attachments"""
        if obj.file_attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file_attachment.url)
            return obj.file_attachment.url
        return None
    
    def get_is_own_message(self, obj):
        """Check if the message belongs to the current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user
        return False


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new messages
    """
    class Meta:
        model = Message
        fields = [
            'message_type', 'message_body', 'file_attachment', 'reply_to'
        ]
    
    def validate(self, data):
        """Validate message data"""
        message_type = data.get('message_type', 'text')
        message_body = data.get('message_body', '')
        file_attachment = data.get('file_attachment')
        
        # Text messages must have content
        if message_type == 'text' and not message_body.strip():
            raise serializers.ValidationError("Text messages cannot be empty.")
        
        # File messages must have attachments
        if message_type in ['image', 'file', 'audio', 'video'] and not file_attachment:
            raise serializers.ValidationError(f"{message_type.title()} messages must include a file attachment.")
        
        return data


class ConversationParticipantSerializer(serializers.ModelSerializer):
    """
    Serializer for conversation participants
    """
    user = UserMinimalSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversationParticipant
        fields = [
            'id', 'user', 'role', 'joined_at', 'last_read_at', 
            'is_muted', 'is_active', 'unread_count'
        ]
        read_only_fields = ['id', 'joined_at']
    
    def get_unread_count(self, obj):
        """Get unread message count for this participant"""
        return obj.conversation.messages.filter(
            sent_at__gt=obj.last_read_at,
            is_deleted=False
        ).exclude(sender=obj.user).count()


class ConversationSerializer(serializers.ModelSerializer):
    """
    Main Conversation serializer with nested relationships
    """
    participants = ConversationParticipantSerializer(
        source='conversation_participants', 
        many=True, 
        read_only=True
    )
    created_by = UserMinimalSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    display_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'title', 'conversation_type', 'participants',
            'created_by', 'created_at', 'updated_at', 'is_active',
            'last_message', 'unread_count', 'participant_count',
            'display_name', 'display_image'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        """Get the most recent message in the conversation"""
        last_message = obj.get_last_message()
        if last_message:
            return {
                'message_id': last_message.message_id,
                'sender': UserMinimalSerializer(last_message.sender).data,
                'message_type': last_message.message_type,
                'message_body': last_message.message_body[:100] + "..." if len(last_message.message_body) > 100 else last_message.message_body,
                'sent_at': last_message.sent_at,
                'is_deleted': last_message.is_deleted
            }
        return None
    
    def get_unread_count(self, obj):
        """Get unread count for the current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.get_unread_count(request.user)
        return 0
    
    def get_participant_count(self, obj):
        """Get total number of active participants"""
        return obj.conversation_participants.filter(is_active=True).count()
    
    def get_display_name(self, obj):
        """Get display name for the conversation"""
        if obj.conversation_type == 'group' and obj.title:
            return obj.title
        
        # For direct messages, show the other participant's name
        request = self.context.get('request')
        if request and request.user.is_authenticated and obj.conversation_type == 'direct':
            other_participant = obj.participants.exclude(user_id=request.user.user_id).first()
            if other_participant:
                return other_participant.get_full_name() or other_participant.username
        
        return f"Conversation {str(obj.conversation_id)[:8]}"
    
    def get_display_image(self, obj):
        """Get display image for the conversation"""
        # For direct messages, use the other participant's profile picture
        request = self.context.get('request')
        if request and request.user.is_authenticated and obj.conversation_type == 'direct':
            other_participant = obj.participants.exclude(user_id=request.user.user_id).first()
            if other_participant and other_participant.profile_picture:
                return request.build_absolute_uri(other_participant.profile_picture.url)
        
        # For group chats, could implement group image logic here
        return None


class ConversationDetailSerializer(ConversationSerializer):
    """
    Detailed Conversation serializer that includes recent messages
    """
    recent_messages = serializers.SerializerMethodField()
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['recent_messages']
    
    def get_recent_messages(self, obj):
        """Get recent messages in the conversation"""
        recent_messages = obj.messages.filter(is_deleted=False)[:20]
        return MessageSerializer(
            recent_messages, 
            many=True, 
            context=self.context
        ).data


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new conversations
    """
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Conversation
        fields = ['title', 'conversation_type', 'participant_ids']
    
    def validate(self, data):
        """Validate conversation creation data"""
        conversation_type = data.get('conversation_type', 'direct')
        participant_ids = data.get('participant_ids', [])
        
        if conversation_type == 'direct' and len(participant_ids) != 1:
            raise serializers.ValidationError(
                "Direct messages must have exactly one other participant."
            )
        
        if conversation_type == 'group' and len(participant_ids) < 1:
            raise serializers.ValidationError(
                "Group conversations must have at least one other participant."
            )
        
        # Validate that all participant IDs exist
        existing_users = User.objects.filter(user_id__in=participant_ids)
        if len(existing_users) != len(participant_ids):
            raise serializers.ValidationError(
                "One or more participant IDs are invalid."
            )
        
        return data
    
    def create(self, validated_data):
        """Create a new conversation with participants"""
        participant_ids = validated_data.pop('participant_ids', [])
        request = self.context.get('request')
        
        # Create the conversation
        conversation = Conversation.objects.create(
            created_by=request.user,
            **validated_data
        )
        
        # Add the creator as a participant
        ConversationParticipant.objects.create(
            conversation=conversation,
            user=request.user,
            role='owner' if validated_data.get('conversation_type') == 'group' else 'member'
        )
        
        # Add other participants
        for user_id in participant_ids:
            user = User.objects.get(user_id=user_id)
            ConversationParticipant.objects.create(
                conversation=conversation,
                user=user,
                role='member'
            )
        
        return conversation


class MessageReactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating message reactions
    """
    class Meta:
        model = MessageReaction
        fields = ['reaction_type']
    
    def create(self, validated_data):
        """Create or update a message reaction"""
        message = self.context['message']
        user = self.context['request'].user
        
        # Remove existing reaction of the same type if it exists
        MessageReaction.objects.filter(
            message=message,
            user=user,
            reaction_type=validated_data['reaction_type']
        ).delete()
        
        # Create new reaction
        return MessageReaction.objects.create(
            message=message,
            user=user,
            **validated_data
        )