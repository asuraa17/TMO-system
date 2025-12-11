from django.shortcuts import redirect
from django.urls import reverse

class AuthenticationMiddleware:
    """
    Middleware to redirect authenticated users away from login and register page
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # paths that authenticated users should access
        restricted_paths = [
            reverse("users:buyer_register"),
            reverse("users:buyer_login"),
        ]

        if request.user.is_authenticated and request.path in restricted_paths:

            if hasattr(request.user, 'role') and request.user.role == 'buyer':
                    return redirect(reverse("users:buyer_home"))
                
            elif hasattr(request.user, 'role'):
                    return redirect(reverse("users:dashboard"))

        response = self.get_response(request)
        return response