"""
Utility functions for building frontend links and sending account-related emails.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.auth import get_user_model
from ..tokens import activation_token_generator, password_reset_token_generator

User = get_user_model()


def _frontend_link(path, uidb64, token):
    """
    Build a frontend URL with encoded user id and token as query parameters.

    Args:
        path (str): Relative path on the frontend application.
        uidb64 (str): Base64-encoded user ID.
        token (str): Token associated with the user.

    Returns:
        str: Fully qualified frontend URL.
    """
    base = settings.FRONTEND_URL.rstrip("/")
    path = path if path.startswith("/") else f"/{path}"
    return f"{base}{path}?uid={uidb64}&token={token}"


def build_activation_link(user):
    """
    Create an activation link for the given user.

    Args:
        user (User): User instance for which to build the activation link.

    Returns:
        tuple[str, str, str]: A tuple containing the activation link,
            the base64-encoded user ID, and the activation token.
    """
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = activation_token_generator.make_token(user)
    return _frontend_link(settings.EMAIL_VERIFICATION_PATH, uidb64, token), uidb64, token


def build_password_reset_link(user):
    """
    Create a password reset link for the given user.

    Args:
        user (User): User instance for which to build the password reset link.

    Returns:
        tuple[str, str, str]: A tuple containing the reset link,
            the base64-encoded user ID, and the password reset token.
    """
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token_generator.make_token(user)
    return _frontend_link(settings.PASSWORD_RESET_PATH, uidb64, token), uidb64, token


def _send_templated_email(subject, to_email, template_base_name, context):
    """
    Send a multipart email using text and HTML templates.

    Args:
        subject (str): Email subject line.
        to_email (str): Recipient email address.
        template_base_name (str): Base name of the templates (without extension).
        context (dict): Context data for rendering the templates.

    Raises:
        Exception: Propagates exceptions if sending fails.
    """
    txt_template = f"emails/{template_base_name}.txt"
    html_template = f"emails/{template_base_name}.html"

    text_content = render_to_string(txt_template, context)
    html_content = render_to_string(html_template, context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)


def send_activation_email(user):
    """
    Send an account activation email to the given user.

    Args:
        user (User): User instance that should receive the activation email.
    """
    link, uidb64, token = build_activation_link(user)

    context = {
        "user": user,
        "activation_link": link,
        "uid": uidb64,
        "token": token,
    }

    _send_templated_email(
        subject="Activate your Videoflix account",
        to_email=user.email,
        template_base_name="account_activation",
        context=context,
    )


def send_password_reset_email(user):
    """
    Send a password reset email to the given user.

    Args:
        user (User): User instance that should receive the password reset email.
    """
    link, uidb64, token = build_password_reset_link(user)

    context = {
        "user": user,
        "reset_link": link,
        "uid": uidb64,
        "token": token,
    }

    _send_templated_email(
        subject="Reset your Videoflix password",
        to_email=user.email,
        template_base_name="password_reset",
        context=context,
    )
