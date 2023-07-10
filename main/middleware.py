from django.shortcuts import redirect
from django.urls import resolve, reverse

class AuthenticationMiddleware:
    URLS = [
        'login', 
        'forgot_password', 
        'register',  
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            current_url_name = resolve(request.path_info).url_name
            if current_url_name not in self.URLS:
                return redirect('login')  # Replace with your login URL name

        response = self.get_response(request)
        return response