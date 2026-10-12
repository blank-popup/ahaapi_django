from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from ahaapi.devapi import views

app_name = "devapi"

urlpatterns = [
    # Health check
    path("health/", views.HealthAPIView.as_view(), name="health"),

    # Access control tests
    path("public/", views.PublicAPIView.as_view(), name="public"),
    path("protected/", views.ProtectedAPIView.as_view(), name="protected"),
    path("admin/", views.AdminAPIView.as_view(), name="admin"),
    path("permissions/", views.PermissionsAPIView.as_view(), name="permissions"),

    # Logging test
    path("log/", views.LogAPIView.as_view(), name="log"),

    # JWT authentication
    path(
        "auth/token/",
        TokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),
    path(
        "auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]
