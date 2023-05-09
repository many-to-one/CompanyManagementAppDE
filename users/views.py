from base64 import urlsafe_b64decode
from typing import Any, Dict
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, View 
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode

from .utils import forgot_password_mail

from .forms import CustomUserChangeForm, CustomUserCreationForm, \
                   AuthenticationForm, ForgotPassword

from .models import CustomUser


# def success(request):
#     return render(request, 'success.html')

# class Login(LoginView):
#     authentication_form = CustomAuthenticationForm
#     redirect_authenticated_user = True


class Register(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'register.html'


class Login(LoginView):
    # in settings.py
    # LOGIN_REDIRECT_URL = "users:profile"
    redirect_authenticated_user = True
    form_class = AuthenticationForm
    template_name = 'login.html'
    
    # def get_success_url(self):
    #     return reverse_lazy('tasks') 
    
    def form_invalid(self, form):
        messages.error(self.request,'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))
    

# class Logout(View):
#     def logout(self, request):
#         logout(request)
#         return redirect('home')


def logout_view(request):
    logout(request)
    messages.success(request, 'Log out')
    return redirect('login')


class UpdateUser(UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('home')
    template_name = 'update_password.html'


import datetime
def forgotPassword(request):
    
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            user = CustomUser.objects.get(email=email)
            now = datetime.datetime.now()
            forgot_password_mail(email, user)
            # return redirect('change_password')
    except Exception as e:
        print(e)
    return render(request, 'forgot_password.html')


def changePassword(request, token, uidb64):
    token_time = f'{token[36:40]}-{token[76:78]}-{token[114:116]} {token[152:154]}:{token[190:192]}'
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    one_minute = datetime.timedelta(minutes=1)
    new_time = str(time_now) + str(one_minute)
    # print(token_time)
    # print(type(token_time))
    # print(time_now)
    # print(type(time_now))
    # print(new_time[:-7])
    # print(type(new_time[:-7]))
    
    try:
        if request.method == 'POST' and token_time == str(time_now) or request.method == 'POST' and str(time_now) == str(new_time[:-7]):
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            user_id = urlsafe_base64_decode(uidb64)
            user = CustomUser.objects.get(id=user_id)
            if password1 != password2:
                messages.add_message(request, messages.error, "Hasła nie są podobne do siebie")
                # messages.error(request, 'Hasła nie są podobne do siebie')
                return redirect('login')
            elif token == user.fp_token:
                print('Tokeny podobne do siebie')
                messages.add_message(request, messages.error, "Token is used")
                return redirect('login')
            user.set_password(password2)
            user.fp_token = token
            user.save()
            messages.add_message(request, messages.error, "Hasło zostało zmienione")
            return redirect('login')
        messages.add_message(request, messages.error, "Token is invalid")
        return redirect('login')
    except Exception as e:
        print(e)
    return render(request, 'change_password.html')



class Profile(DetailView):
    model = CustomUser
    context_object_name = 'user'
    template_name = 'profile.html'

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.kwargs['pk'])
    