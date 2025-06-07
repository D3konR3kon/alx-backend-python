from rest_framework import permissions
from .models import ConversationParticipant

class IsParticipant(permissions.BasePermission):
    """
    Custom permission to allow only active participants of a conversation
    to view, send, update, or delete messages.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission:
        Checks if user is an active participant in the conversation.
        """

        if hasattr(obj, 'conversation'):
            conversation = obj.conversation
        elif hasattr(obj, 'conversation_participants'):
            conversation = obj
        else:
            return False

        return ConversationParticipant.objects.filter(
            conversation=conversation,
            user=request.user,
            is_active=True
        ).exists()
