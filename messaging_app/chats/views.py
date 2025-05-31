# chats/views.py

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

class ChatListView(generics.ListAPIView):
    """
    Basic chat list view - placeholder for your messaging functionality
    """
    
    def get(self, request, *args, **kwargs):
        return Response({
            'message': 'Chat API is working!',
            'status': 'success'
        }, status=status.HTTP_200_OK)