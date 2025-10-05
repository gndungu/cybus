# your_project/middleware.py
from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve

EXEMPT_URLS = [
    '/register/',
    '/login/',
    '/admin/',  # optional
    '/password_reset/',
    '/password_reset_done/'
    '/password_reset_confirm/'
    '/password_reset_complete/'
]

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        if not request.user.is_authenticated and not any(path.startswith(url) for url in EXEMPT_URLS):
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)
