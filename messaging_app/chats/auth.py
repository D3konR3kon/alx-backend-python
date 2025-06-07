from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    """
    Extends JWTAuthentication to:
    - Automatically update last_seen
    - Reject inactive users
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, validated_token = result
    
        if not user.is_active:
            raise AuthenticationFailed('User is inactive')

        user.update_last_seen()

        return (user, validated_token)
