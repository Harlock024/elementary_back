from django.http import HttpResponseForbidden
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

class IsAdmin(BasePermission):
    """
    Custom permission to only allow admin users to access certain views.
    """

    allowed_roles = ['Admin',"directora"]
    def has_permission(self, request, view):
        return ( request.user and request.user.is_authenticated and 
                getattr(request.user, 'role', None) in self.allowed_roles
                )


class RoleMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.protected_paths = ['/students/']


def __call__(self, request):
        if request.path in self.protected_paths:
            if not (request.user.is_authenticated and request.user.role in ['admin', 'director']):
                return Response("No tienes acceso a este recurso.")
        return self.get_response(request)
