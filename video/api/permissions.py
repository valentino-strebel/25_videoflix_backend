"""
Custom authentication backend for validating JWT access tokens stored in cookies.
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class CookieJWTAuthentication(BaseAuthentication):
    """
    Authentication class that extracts a JWT access token from the request's cookies.
    Validates the token using SimpleJWT and returns the associated active user.
    """

    def authenticate(self, request: Request):
        """
        Attempt to authenticate the user via the 'access_token' cookie.

        Args:
            request (Request): Incoming DRF request object.

        Returns:
            tuple: (User, None) if authentication succeeds.
            None: If no token cookie is present.

        Raises:
            AuthenticationFailed: If the token is invalid or user cannot be retrieved.
        """
        raw = request.COOKIES.get("access_token")
        if not raw:
            return None

        try:
            token = AccessToken(raw)
            user_id = token.get("user_id")
            user = User.objects.get(id=user_id, is_active=True)
        except Exception:
            raise exceptions.AuthenticationFailed("Not authenticated.")

        return (user, None)


AuthenticatedOnly = {
    """
    Settings shortcut for applying cookie-based JWT authentication and requiring
    that the user is authenticated.
    """
    "authentication_classes": [CookieJWTAuthentication],
    "permission_classes": [IsAuthenticated],
}
