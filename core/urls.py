from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(("authentication.urls", "authentication"), namespace="authentication")),
    path("api/", include(("video.urls", "video"), namespace="video")),
    path("django-rq/", include("django_rq.urls")),
]
