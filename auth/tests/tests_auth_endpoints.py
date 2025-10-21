import base64
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


def create_user(email="user@example.com", password="Password123!"):
    return User.objects.create_user(email=email, password=password)


def test_register_sends_activation(client: APIClient, settings):
    url = reverse("authapp:register")
    res = client.post(url, {"email": "new@example.com", "password": "Password123!", "confirmed_password": "Password123!"}, format="json")
    assert res.status_code == 201
    assert "user" in res.data


def test_activate_flow(client: APIClient):
    user = create_user()
    from auth.tokens import activation_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = activation_token_generator.make_token(user)

    url = reverse("authapp:activate", args=[uidb64, token])
    res = client.get(url)
    assert res.status_code == 200
    user.refresh_from_db()
    assert user.is_active is True


def test_login_sets_cookies(client: APIClient):
    user = create_user()
    user.is_active = True
    user.save()
    url = reverse("authapp:login")
    res = client.post(url, {"email": user.email, "password": "Password123!"}, format="json")
    assert res.status_code == 200
    assert "access_token" in res.cookies
    assert "refresh_token" in res.cookies


def test_token_refresh_requires_cookie(client: APIClient):
    url = reverse("authapp:token_refresh")
    res = client.post(url, {})
    assert res.status_code == 400


def test_password_reset_returns_200_always(client: APIClient, mailoutbox):
    url = reverse("authapp:password_reset")
    res = client.post(url, {"email": "nobody@example.com"}, format="json")
    assert res.status_code == 200


def test_password_confirm_flow(client: APIClient):
    user = create_user()
    user.is_active = True
    user.save()
    from auth.tokens import password_reset_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token_generator.make_token(user)
    url = reverse("authapp:password_confirm", args=[uidb64, token])
    res = client.post(url, {"new_password": "NewPass123!", "confirm_password": "NewPass123!"}, format="json")
    assert res.status_code == 200
    assert "successfully" in res.data["detail"].lower()
