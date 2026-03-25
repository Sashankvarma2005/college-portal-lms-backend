from django.conf import settings

from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Global exception mapping for auth-related failures.
    """
    # Let DRF build the default structure where possible.
    response = exception_handler(exc, context)
    if response is not None:
        return response

    # Fallbacks (rare).
    if isinstance(exc, AuthenticationFailed):
        return Response({"detail": str(exc)}, status=401)
    if isinstance(exc, PermissionDenied):
        return Response({"detail": str(exc)}, status=403)

    if getattr(settings, "DEBUG", False):
        return Response(
            {"detail": str(exc), "type": exc.__class__.__name__},
            status=500,
        )

    return Response({"detail": "Server error."}, status=500)

