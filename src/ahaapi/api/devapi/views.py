import logging

from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthAPIView(APIView):
    """Check whether the API server is responding."""

    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request):
        logger.debug("Health check debug message.")
        logger.info("Health check info message.")
        logger.warning("Health check warning message.")
        logger.error("Health check error message.")
        logger.critical("Health check critical message.")
        try:
            raise ValueError("Test exception")
        except Exception:
            logger.exception("An exception occurred")

        logger.exception("Health check exception message.")

        return Response({
            "status": "ok",
            "message": "Development API is running.",
            "version": "v1",
        })


class PublicAPIView(APIView):
    """Provide an endpoint accessible without authentication."""

    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request):
        return Response({
            "endpoint": "public",
            "message": "Authentication is not required.",
            "authenticated": request.user.is_authenticated,
        })


class ProtectedAPIView(APIView):
    """Allow access only to authenticated users."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "endpoint": "protected",
            "message": "Authenticated access granted.",
            "user": request.user.get_username(),
        })


class AdminAPIView(APIView):
    """Allow access only to staff users."""

    permission_classes = (IsAdminUser,)

    def get(self, request):
        user = request.user

        return Response({
            "endpoint": "admin",
            "message": "Staff access granted.",
            "user": user.get_username(),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        })


class PermissionsAPIView(APIView):
    """Return the authenticated user's groups and permissions."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        return Response({
            "username": user.get_username(),
            "is_authenticated": user.is_authenticated,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "groups": list(
                user.groups.values_list("name", flat=True)
            ),
            "permissions": sorted(user.get_all_permissions()),
        })


class LogAPIView(APIView):
    """Write a log entry for the authenticated user."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        username = request.user.get_username()

        logger.info(
            "Development log API accessed: user=%s",
            username,
        )

        return Response({
            "endpoint": "log",
            "message": "Log event recorded.",
            "user": username,
        })
