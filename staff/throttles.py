from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """IP-based throttle dedicated to the public JWT login endpoint."""

    scope = "jwt_login"

    def get_rate(self):
        return settings.JWT_LOGIN_RATE

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}
