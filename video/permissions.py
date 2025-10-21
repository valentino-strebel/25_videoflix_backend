from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):
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


AuthenticatedOnly = [CookieJWTAuthentication], [IsAuthenticated]
