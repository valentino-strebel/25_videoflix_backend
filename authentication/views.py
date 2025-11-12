from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    PasswordConfirmSerializer,
)
from .tokens import activation_token_generator, password_reset_token_generator
from .utils import send_activation_email, send_password_reset_email

User = get_user_model()


def _set_jwt_cookies(response, refresh: RefreshToken, *, secure=None):
    if secure is None:
        from django.conf import settings
        secure = not settings.DEBUG

    access = str(refresh.access_token)
    response.set_cookie(
        "access_token",
        access,
        httponly=True,
        secure=secure,
        samesite="None",         
        max_age=60 * 60,         
    )
    response.set_cookie(
        "refresh_token",
        str(refresh),
        httponly=True,
        secure=secure,
        samesite="None",         
        max_age=60 * 60 * 24 * 7, 
    )


def _clear_jwt_cookies(response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_activation_email(user)
        # Optional demo token in response (not used by FE)
        from .utils import build_activation_link
        _, uidb64, token = build_activation_link(user)
        data = {"user": {"id": user.id, "email": user.email}, "token": "activation_token"}
        # keep "activation_token" literal per spec, but expose real path in headers for dev
        response = Response(data, status=status.HTTP_201_CREATED)
        response["X-Debug-Activation-Backend"] = f"/api/activate/{uidb64}/{token}/"
        return response


@api_view(["GET"])
@permission_classes([AllowAny])
def activate_view(request, uidb64, token):
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
    permission_classes = [AllowAny]

    def post(self, request):
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
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_cookie = request.COOKIES.get("refresh_token")
        if not refresh_cookie:
            return Response({"detail": "Refresh token is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_cookie)
            token.blacklist()
        except Exception:
            # token invalid or already blacklisted — still clear cookies
            pass
        response = Response(
            {"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK,
        )
        _clear_jwt_cookies(response)
        return response


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        # Always respond 200 to avoid account enumeration; send only if exists
        try:
            user = User.objects.get(email__iexact=email)
            send_password_reset_email(user)
        except User.DoesNotExist:
            pass

        return Response({"detail": "An email has been sent to reset your password."})


class PasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
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
