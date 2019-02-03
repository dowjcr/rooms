"""
MIDDLEWARE
Defines classes to be executed before view loads.
Author Cameron O'Connor
"""

from django.conf import settings
from django.http import HttpResponseRedirect
from re import compile
from .models import Student, AdminUser, ProxyUser
from .views import error, set_first_name


# =============== AUTH REQUIRED ==================
# Checks that user is logged in, and is a registered
# student, or is accessing admin dashboard.

class AuthRequiredMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
        if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
            EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]
        response = self.get_response(request)
        # Check whether user is authenticated.
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return HttpResponseRedirect('/roomballot/welcome')
            else:
                return response
        # Check that user is registered as a student, excluding admin pages.
        ADMIN_URLS = [compile('roomballot/admin'), compile('admin')]
        try:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in ADMIN_URLS):
                student = Student.objects.get(user_id=request.user.username)
                if not student.name_set:
                    return set_first_name(request)
        except Student.DoesNotExist:
            try:
                PROXY_URLS = [compile('roomballot/staircase'), compile('roomballot/proxy'), compile('roomballot/room')]
                ProxyUser.objects.get(user_id=request.user.username)
                if any(m.match(request.path_info.lstrip('/')) for m in PROXY_URLS):
                    return response
                else:
                    return HttpResponseRedirect('/roomballot/proxy')
            except ProxyUser.DoesNotExist:
                # Redirects to admin page if only admin user.
                try:
                    AdminUser.objects.get(user_id=request.user.username)
                    return HttpResponseRedirect('/roomballot/admin')
                except AdminUser.DoesNotExist:
                    return error(request, 906)
        return response