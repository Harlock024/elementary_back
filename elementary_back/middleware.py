from rest_framework.permissions import BasePermission
from django.utils.deprecation import MiddlewareMixin


class IsAdmin(BasePermission):
    """
    Custom permission to only allow admin users to access certain views.
    """

    allowed_roles = ["Admin", "Superuser", "Principal"]

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or getattr(request.user, "role", None) in self.allowed_roles
            )
        )

class RoleScopeMiddleware(MiddlewareMixin):
    def process_view(self,request,view_func,view_args,view_kwargs):
        staff = request.user

        if not staff.is_authenticated:
            request.scope = None
            return None

        if staff.is_superuser or staff.role in IsAdmin.allowed_roles:
            request.scope = 'all'
        elif staff.role == 'Teacher':
            request.scope = 'Teacher'
        else:
            request.scope = None

        return None
