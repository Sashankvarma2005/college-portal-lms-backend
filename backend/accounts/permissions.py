from rest_framework.permissions import BasePermission

from .exceptions import ForbiddenException, UnauthorizedException

class RoleBasedPermission(BasePermission):
    """
    Permission based on JWT 'role' claim.

    Usage:
      class SomeView(APIView):
          required_roles = ["STUDENT"]
          permission_classes = [RoleBasedPermission]
    """

    def has_permission(self, request, view) -> bool:
        required_roles = getattr(view, "required_roles", None)
        if not required_roles:
            return True

        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            raise UnauthorizedException()

        role = getattr(user, "role", None)
        if role not in required_roles:
            raise ForbiddenException()

        return True


class RoleBasedMethodPermission(BasePermission):
    """
    RBAC with different role requirements for read vs write HTTP methods.

    Configure on the view:
      required_roles_read = [...]
      required_roles_write = [...]
    """

    required_roles_read: list[str] = []
    required_roles_write: list[str] = []

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            raise UnauthorizedException()

        role = getattr(user, "role", None)
        if role is None:
            raise UnauthorizedException()

        if request.method in ("GET", "HEAD", "OPTIONS"):
            required = getattr(view, "required_roles_read", self.required_roles_read)
        else:
            required = getattr(view, "required_roles_write", self.required_roles_write)

        if not required:
            # If nothing configured, default to forbid.
            raise ForbiddenException()

        if role not in required:
            raise ForbiddenException()

        return True

