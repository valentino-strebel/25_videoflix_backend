from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(("auth.urls", "auth"), namespace="auth")),
    path("api/", include(("auth.urls", "auth"), namespace="auth")),
    path("api/", include(("video.urls", "video"), namespace="video")),
]
