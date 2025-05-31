# chats/urls.py

from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    path('', views.ChatListView.as_view(), name='chat-list'),
]