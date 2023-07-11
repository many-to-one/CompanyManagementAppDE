from django.utils import timezone
from django.shortcuts import redirect
from django.urls import resolve
from django.contrib.auth import logout

from django.apps import apps

class AuthenticationMiddleware:

    def get_model_from_string(model_string):
        app_label, model_name = model_string.split('.')
        return apps.get_model(app_label, model_name)

    URLS = [
        'login', 
        'forgot_password', 
        'register', 
        'change_password', 
        'accept_ip_address',
        'block_ip_address',
        'chack_email',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # The user can't use any url if it isn't authenticated
        if not request.user.is_authenticated:
            current_url_name = resolve(request.path_info).url_name
            if current_url_name not in self.URLS:
                return redirect('login')
        # The user will be loging out if the time of he's token
        # will be expired
        elif request.user.token_expiration < timezone.now():
            # Getting BlacklistToken model from users.app
            BlacklistToken = apps.get_model('users', 'BlacklistToken')
            black_list = BlacklistToken(
                token=request.user.fp_token
            )
            black_list.save()
            logout(request)
            return redirect('login')

        # elif request.user.fp_token == None:
        #     return redirect('login')

        response = self.get_response(request)
        return response