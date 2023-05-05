from typing import Any, Dict
from django.db import models
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView 
from django.contrib.auth.views import LoginView
from django.contrib import messages

from .forms import CustomUserCreationForm, AuthenticationForm

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


class Profile(DetailView):
    model = CustomUser
    context_object_name = 'user'
    template_name = 'profile_view.html'

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.kwargs['pk'])