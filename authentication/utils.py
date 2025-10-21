from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .tokens import activation_token_generator, password_reset_token_generator

User = get_user_model()


def _frontend_link(path, uidb64, token):
    base = settings.FRONTEND_URL.rstrip("/")
    path = path if path.startswith("/") else f"/{path}"
    return f"{base}{path}?uid={uidb64}&token={token}"


def build_activation_link(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = activation_token_generator.make_token(user)
    return _frontend_link(settings.EMAIL_VERIFICATION_PATH, uidb64, token), uidb64, token


def build_password_reset_link(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token_generator.make_token(user)
    return _frontend_link(settings.PASSWORD_RESET_PATH, uidb64, token), uidb64, token


def send_activation_email(user):
    link, _, _ = build_activation_link(user)
    subject = "Activate your Videoflix account"
    message = f"Click the link to activate your account: {link}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_password_reset_email(user):
    link, _, _ = build_password_reset_link(user)
    subject = "Reset your Videoflix password"
    message = f"Click the link to reset your password: {link}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
