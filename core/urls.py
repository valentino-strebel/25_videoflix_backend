from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(("authentication.urls", "authentication"), namespace="authentication")),
    path("api/", include(("video.urls", "video"), namespace="video")),
    path("django-rq/", include("django_rq.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)