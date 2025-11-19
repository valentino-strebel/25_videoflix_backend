"""
Views for user authentication, JWT handling, and password management.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    PasswordConfirmSerializer,
)
from ..tokens import activation_token_generator, password_reset_token_generator
from .utils import send_activation_email, send_password_reset_email

User = get_user_model()


def _set_jwt_cookies(response, refresh: RefreshToken, *, secure=None):
    """
    Set HTTP-only cookies for access and refresh JWT tokens.

    Args:
        response (Response): DRF response object to which cookies will be added.
        refresh (RefreshToken): Refresh token instance.
        secure (bool | None): Whether to mark cookies as secure. Defaults to
            the inverse of settings.DEBUG.
    """
    if secure is None:
        secure = not settings.DEBUG

    access = str(refresh.access_token)

    samesite_value = "None"
    if settings.DEBUG and not secure:
        samesite_value = "Lax"

    response.set_cookie(
        "access_token",
        access,
        httponly=True,
        secure=secure,
        samesite=samesite_value,
        max_age=60 * 60,
    )
    response.set_cookie(
        "refresh_token",
        str(refresh),
        httponly=True,
        secure=secure,
        samesite=samesite_value,
        max_age=60 * 60 * 24 * 7,
    )


def _clear_jwt_cookies(response):
    """
    Remove JWT cookies from the response.

    Args:
        response (Response): DRF response object from which cookies will be removed.
    """
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


class RegisterView(APIView):
    """
    Handle user registration and trigger account activation email.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Create a new user and send an activation email.

        Returns:
            Response: 201 response with user data and debug activation header.
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_activation_email(user)

        from .utils import build_activation_link

        _, uidb64, token = build_activation_link(user)
        data = {"user": {"id": user.id, "email": user.email}, "token": "activation_token"}
        response = Response(data, status=status.HTTP_201_CREATED)
        response["X-Debug-Activation-Backend"] = f"/api/activate/{uidb64}/{token}/"
        return response


@api_view(["GET"])
@permission_classes([AllowAny])
def activate_view(request, uidb64, token):
    """
    Activate a user account using a base64 user ID and activation token.

    Args:
        request: HTTP request instance.
        uidb64 (str): Base64-encoded user ID.
        token (str): Activation token.

    Returns:
        Response: 200 if activation succeeds, 400 otherwise.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return Response({"message": "Activation failed."}, status=status.HTTP_400_BAD_REQUEST)

    if activation_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)

    return Response({"message": "Activation failed."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Authenticate a user and issue JWT tokens stored in cookies.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Validate login credentials and set JWT cookies.

        Returns:
            Response: 200 response with user information on success.
        """
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        response = Response(
            {"detail": "Login successful", "user": {"id": user.id, "username": user.email}},
            status=status.HTTP_200_OK,
        )
        _set_jwt_cookies(response, refresh, secure=request.is_secure())
        return response


class LogoutView(APIView):
    """
    Log out a user by blacklisting the refresh token and clearing cookies.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Blacklist the refresh token from cookies and clear authentication cookies.

        Returns:
            Response: 200 on success, 400 if refresh token cookie is missing.
        """
        refresh_cookie = request.COOKIES.get("refresh_token")
        if not refresh_cookie:
            return Response({"detail": "Refresh token is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_cookie)
            token.blacklist()
        except Exception:
            pass

        response = Response(
            {"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK,
        )
        _clear_jwt_cookies(response)
        return response


class TokenRefreshView(APIView):
    """
    Issue a new access token from a valid refresh token stored in cookies.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Refresh the access token using the refresh token cookie.

        Returns:
            Response: 200 with new access token, 400 or 401 on error.
        """
        refresh_cookie = request.COOKIES.get("refresh_token")
        if not refresh_cookie:
            return Response({"detail": "Refresh token is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_cookie)
            access = str(refresh.access_token)
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({"detail": "Token refreshed", "access": access}, status=status.HTTP_200_OK)
        response.set_cookie(
            "access_token",
            access,
            httponly=True,
            secure=(not settings.DEBUG),
            samesite="None",
            max_age=60 * 60,
        )
        return response


class PasswordResetRequestView(APIView):
    """
    Initiate a password reset by sending an email if the address exists.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Accept an email and send a password reset message if a user is found.

        Returns:
            Response: 200 response regardless of user existence.
        """
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email__iexact=email)
            send_password_reset_email(user)
        except User.DoesNotExist:
            pass

        return Response({"detail": "An email has been sent to reset your password."})


class PasswordConfirmView(APIView):
    """
    Confirm a password reset using a token and update the user's password.
    """

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """
        Validate the reset token and set a new password for the user.

        Args:
            uidb64 (str): Base64-encoded user ID.
            token (str): Password reset token.

        Returns:
            Response: 200 on successful password reset, 400 on invalid token or user.
        """
        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST)

        if not password_reset_token_generator.check_token(user, token):
            return Response({"detail": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Your Password has been successfully reset."}, status=status.HTTP_200_OK)
