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
            reverse("users:all_login"),
        ]

        if request.user.is_authenticated and request.path in restricted_paths:

            if hasattr(request.user, 'role'):
                role = request.user.role

                if role == 'buyer':
                    return redirect(reverse("users:buyer_home"))
                
                elif role == 'tmo_officer':
                    try:
                        officer = request.user.tmo_officer_profile
                        if not officer.has_changed_password:
                            return redirect(reverse("tmo:change_password"))
                        else:
                            return redirect(reverse("tmo:dashboard"))
                    except Exception:
                        return redirect(reverse("tmo:dashboard"))
                
                elif role == 'showroom':
                    try:
                        showroom = request.user.showroom_profile
                        if showroom.verification_status == 'pending':
                            # Allow them to see their dashboard even if pending
                            pass
                        return redirect(reverse("showroom:dashboard"))
                    except Exception:
                        return redirect(reverse("showroom:dashboard"))
                else:
                    return redirect(reverse("users:dashboard"))
            else:
                return redirect(reverse("users:dashboard"))                

        response = self.get_response(request)
        return response