"""
Django settings for the core project.

Loads environment-based configuration for security, database, Redis, email,
CORS, JWT authentication, static/media handling, and application behavior.
"""

from pathlib import Path
from decouple import config
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _split_env(name, default=""):
    """
    Split a comma-separated environment variable into a cleaned list of values.

    Args:
        name (str): Environment variable key.
        default (str): Fallback value if the variable is missing.

    Returns:
        list[str]: List of trimmed strings.
    """
    return [x.strip() for x in config(name, default=default).split(",") if x.strip()]


SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = _split_env("ALLOWED_HOSTS", default="127.0.0.1")

AUTH_USER_MODEL = "authentication.User"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_rq",
    "authentication",
    "video.apps.VideoConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "videoflix_db"),
        "USER": os.environ.get("DB_USER", "videoflix_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", 5432),
    }
}

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB_CACHE = int(os.environ.get("REDIS_DB_CACHE", 1))
REDIS_DB_RQ = int(os.environ.get("REDIS_DB_RQ", 0))

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get(
            "REDIS_LOCATION",
            f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_CACHE}",
        ),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "videoflix",
    }
}

RQ_QUEUES = {
    "default": {
        "HOST": os.environ.get("REDIS_HOST", "redis"),
        "PORT": int(os.environ.get("REDIS_PORT", 6379)),
        "DB": int(os.environ.get("REDIS_DB", 0)),
        "DEFAULT_TIMEOUT": 900,
        "REDIS_CLIENT_KWARGS": {},
    },
}

EMAIL_BACKEND = "core.api.email_backends.MultiEmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=25, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=False, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=EMAIL_HOST_USER or "no-reply@videoflix.local",
)

FRONTEND_URL = config("FRONTEND_URL", default="http://127.0.0.1:5500")
EMAIL_VERIFICATION_PATH = config("EMAIL_VERIFICATION_PATH", default="/verify-email")
PASSWORD_RESET_PATH = config("PASSWORD_RESET_PATH", default="/reset-password")

CORS_ALLOWED_ORIGINS = _split_env(
    "CORS_ALLOWED_ORIGINS",
    default="http://127.0.0.1:5500",
)

CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ["X-Debug-Activation-Backend"]

CSRF_TRUSTED_ORIGINS = _split_env(
    "CSRF_TRUSTED_ORIGINS",
    default="http://127.0.0.1:5500",
)

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=not DEBUG, cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=not DEBUG, cast=bool)
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

HLS_ROOT = str(MEDIA_ROOT / "hls")

VIDEO_ALLOWED_RESOLUTIONS = _split_env(
    "VIDEO_ALLOWED_RESOLUTIONS",
    default="120p,360p,720p,1080p",
)

LOG_LEVEL = config("LOG_LEVEL", default="INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{levelname}] {asctime} {name}: {message}", "style": "{"},
        "simple": {"format": "[{levelname}] {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"}
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
