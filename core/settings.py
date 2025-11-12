"""
Django settings for core project.
"""

from pathlib import Path
from decouple import config
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------- Helpers ----------
def _split_env(name, default=""):
    # Split comma-separated env vars, trimming empties/whitespace
    return [x.strip() for x in config(name, default=default).split(",") if x.strip()]

# ---------- Core ----------
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    default="django-insecure-@#x5h3zj!g+8g1v@2^b6^9$8&f1r7g$@t3v!p4#=g0r5qzj4m3",
)
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,[::1]",
).split(",")

AUTH_USER_MODEL = "authentication.User"

# ---------- Apps ----------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_rq",

    # Local
    "authentication",
    "video.apps.VideoConfig",
]

# ---------- Middleware ----------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    # CORS must be high in the list and before CommonMiddleware
    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

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

# ---------- Database ----------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", default="videoflix_db"),
        "USER": os.environ.get("DB_USER", default="videoflix_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", default="supersecretpassword"),
        "HOST": os.environ.get("DB_HOST", default="db"),
        "PORT": os.environ.get("DB_PORT", default=5432),
    }
}

# ---------- Cache / Redis ----------
REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB_CACHE = int(os.environ.get("REDIS_DB_CACHE", 1))
REDIS_DB_RQ = int(os.environ.get("REDIS_DB_RQ", 0))

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_LOCATION", default="redis://redis:6379/1"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "videoflix",
    }
}

# ---------- RQ Queues ----------
RQ_QUEUES = {
    "default": {
        "HOST": os.environ.get("REDIS_HOST", default="redis"),
        "PORT": os.environ.get("REDIS_PORT", default=6379),
        "DB": os.environ.get("REDIS_DB", default=0),
        "DEFAULT_TIMEOUT": 900,
        "REDIS_CLIENT_KWARGS": {},
    },
}

# ---------- Email ----------
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=25, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or "no-reply@videoflix.local"

# ---------- Frontend link building for emails ----------
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")
EMAIL_VERIFICATION_PATH = config("EMAIL_VERIFICATION_PATH", default="/verify-email")
PASSWORD_RESET_PATH = config("PASSWORD_RESET_PATH", default="/reset-password")

# ---------- CORS / CSRF ----------
# Allow common local dev frontends by default; override with env in deploys.
CORS_ALLOWED_ORIGINS = _split_env(
    "CORS_ALLOWED_ORIGINS",
    default=(
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:4200,"
        "http://127.0.0.1:4200,"
        "https://localhost:3000,"
        "https://127.0.0.1:3000"
    ),
)

# If you use cookies (you do), credentials must be allowed and origin cannot be '*'
CORS_ALLOW_CREDENTIALS = True

# Expose your custom debug header so FE can read it without console errors
CORS_EXPOSE_HEADERS = ["X-Debug-Activation-Backend"]

# CSRF trusted origins must include the exact scheme+host(+port)
CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS",
    (
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:4200,"
        "http://127.0.0.1:4200,"
        "https://localhost:3000,"
        "https://127.0.0.1:3000"
    ),
).split(",")

# ---------- Security ----------
# In production (DEBUG=False), enforce HTTPS and secure cookies by default.
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=not DEBUG, cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=not DEBUG, cast=bool)
# Good defaults for modern browsers
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# ---------- DRF / JWT ----------
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

# ---------- i18n ----------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------- Static & Media ----------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------- Video / HLS ----------
HLS_ROOT = str(MEDIA_ROOT / "hls")
VIDEO_ALLOWED_RESOLUTIONS = _split_env(
    "VIDEO_ALLOWED_RESOLUTIONS", default="120p,360p,720p,1080p"
)

# ---------- Logging ----------
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{levelname}] {asctime} {name}: {message}", "style": "{"},
        "simple": {"format": "[{levelname}] {message}", "style": "{"},
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
