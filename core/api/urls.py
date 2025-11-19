"""
Root URL configuration for the project, including admin, authentication, video,
and background job endpoints.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/",
        include(
            ("authentication.api.urls", "authentication"),
            namespace="authentication"
        ),
    ),
    path(
        "api/",
        include(
            ("video.api.urls", "video"),
            namespace="video"
        ),
    ),
    path("django-rq/", include("django_rq.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
