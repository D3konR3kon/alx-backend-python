from rest_framework import permissions
from .models import ConversationParticipant

class IsParticipant(permissions.BasePermission):
    """
    Allows access only to active participants of the conversation.
    """
    def has_object_permission(self, request, view, obj):
        return ConversationParticipant.objects.filter(
            conversation=obj,
            user=request.user,
            is_active=True
        ).exists()
