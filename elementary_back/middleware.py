from django.http import HttpResponseForbidden, request
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from django.utils.deprecation import MiddlewareMixin


class IsAdmin(BasePermission):
    """
    Custom permission to only allow admin users to access certain views.
    """

    allowed_roles = ['admin']
    def has_permission(self, request, view):
        return ( request.user and request.user.is_authenticated and 
                getattr(request.user, 'role', None) in self.allowed_roles
                )

class RoleScopeMiddleware(MiddlewareMixin):
    def process_view(self,request,view_func,view_args,view_kwargs):
        staff = request.user

        if not staff.is_authenticated:
            request.scope = None;
            return None

        if staff.role == 'admin':
            request.scope = 'all';
        elif staff.role == 'teacher':
            request.scope = 'teacher';
        else:
            request.scope = None;

        return None
