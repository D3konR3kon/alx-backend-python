from rest_framework import permissions
from .models import ConversationParticipant

class IsParticipant(permissions.BasePermission):
    """
    Allows only authenticated users who are active participants of the conversation
    to perform message-related actions.
    """
    allowed_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

    def has_permission(self, request, view):

        return request.user and request.user.is_authenticated and request.method in self.allowed_methods

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
