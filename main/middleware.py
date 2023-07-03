from django.shortcuts import redirect, render
    

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        if not request.user.is_authenticated:
            return render(request, 'login.html')
    
        response = self.get_response(request)
        
        return response