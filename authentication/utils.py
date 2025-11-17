from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
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


def _send_templated_email(subject, to_email, template_base_name, context):
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
