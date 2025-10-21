from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    TokenRefreshView,
    PasswordResetRequestView,
    PasswordConfirmView,
    activate_view,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("activate/<uidb64>/<token>/", activate_view, name="activate"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("password_reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("password_confirm/<uidb64>/<token>/", PasswordConfirmView.as_view(), name="password_confirm"),
]
