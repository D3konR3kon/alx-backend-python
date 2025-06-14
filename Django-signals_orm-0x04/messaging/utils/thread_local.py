import threading

_user = threading.local()

def set_current_user(user):
    _user.value = user

def get_current_user():
    return getattr(_user, 'value', None)

def build_message_tree(message):
    """Recursively build the thread of replies for a message"""
    return {
        'message': message,
        'replies': [
            build_message_tree(reply) for reply in message.replies.all().select_related('sender')
        ]
    }