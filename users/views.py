# from base64 import urlsafe_b64decode
# from typing import Any, Dict
# from django.db import models
# from django.http import HttpRequest, HttpResponse
# from django.forms.models import BaseModelForm
# from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView 
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from datetime import datetime, timedelta
from django.utils import timezone
from .utils import blacklist_token, check_user_ip_mail, create_token, forgot_password_mail
from .forms import CustomUserChangeForm, CustomUserCreationForm, \
                   AuthenticationForm
from .models import BlacklistToken, CustomUser
from django.core.paginator import Paginator


class Register(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'register.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        if user.is_superuser:
            user.acceptation = True
            user.save()
        user.ip_address = {
            'ip': [self.request.META.get('REMOTE_ADDR')],
            'block': [],
            }
        user.save()
        # Creating a new token for loged user
        token = create_token()
        # Checking if the token is not in blacklist
        token_list = BlacklistToken.objects.values_list('token', flat=True)
        if token_list and token in token_list:
            return render(self.request, 'error.html', 
                          context={'error': 'Niepoprawny token po Logowaniu'})
        # Set the expire tme of token (30 min)
        user.fp_token = token
        user.token_expiration = timezone.now() + timedelta(minutes=30)
        user.save()
        return super().form_valid(form)


class Login(LoginView):
    # in settings.py
    # LOGIN_REDIRECT_URL = "main:home"
    redirect_authenticated_user = True
    form_class = AuthenticationForm
    template_name = 'login.html'

    def form_valid(self, form):
        user = form.get_user()
        # if user.is_superuser:
        #     user.acceptation = True
        #     user.save()
        if user.acceptation:
            # Get ip_address of request.user
            ip_address = self.request.META.get('REMOTE_ADDR')
            user.ip_address = {
            'ip': [ip_address],
            'block': [],
            }
            user.save()
            # return super().form_valid(form)
            # List of users IP's
            if user.ip_address:
                stored_ip = user.ip_address.get('ip') 
                if user.ip_address: 
                    block_ip = user.ip_address.get('block') 
             
                # Check if IP address is in list of accepted IP addresses  

                if ip_address in stored_ip:
                    # Creating a new token for loged user
                    token = create_token()
                    # Checking if the token is not in blacklist
                    token_list = BlacklistToken.objects.values_list('token', flat=True)
                    if token in token_list:
                        return render(self.request, 'error.html', 
                                      context={'error': 'Niepoprawny token po Logowaniu'})
                    user.fp_token = token
                    # Set the expire tme of token (30 min)
                    user.token_expiration = timezone.now() + timedelta(minutes=30)
                    user.save()
                    return super().form_valid(form)
            
                # Check if IP address is in list of blocked IP addresses 
                elif block_ip:
                    if ip_address in block_ip:
                        context = {'error': '404'}
                        return render(self.request, 'error.html', context)
                        # return redirect('logout')
                else:
                    check_user_ip_mail(user)
                    return redirect('chack_email')
        else:
            context = {'error': 'Nie zostałeś jeszcze zwerefikowany'}
            return render(self.request, 'error.html', context)
    
    def form_invalid(self, form):
        messages.error(self.request,'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))
    

def block_ip_address(request, token, uidb64):
    user = get_object_or_404(CustomUser,
                             id=urlsafe_base64_decode(uidb64))
    token_time = f'{token[36:40]}-{token[76:78]}-{token[114:116]} {token[152:154]}:{token[190:192]}'
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    one_minute = timedelta(minutes=1)
    new_time = str(time_now) + str(one_minute)
    print('request.method', request.method)
    if request.method == 'GET':
        if token_time == str(time_now) or str(time_now) == str(new_time[:-7]):
            user.ip_address['block'].append(request.META.get('REMOTE_ADDR'))
            user.save()
            return render(request, 'success.html',
                          context={'success': 'Urządzenie zostało zablokowane'})
    else:
        return render(request, 'error.html',
                      context={'error': 'Niewłaściwy token'})
    

def accept_ip_address(request, token, uidb64):
    user = get_object_or_404(CustomUser,
                             id=urlsafe_base64_decode(uidb64))
    token_time = f'{token[36:40]}-{token[76:78]}-{token[114:116]} {token[152:154]}:{token[190:192]}'
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    one_minute = timedelta(minutes=1)
    new_time = str(time_now) + str(one_minute)
    if request.method == 'GET':
        if token_time == str(time_now) or str(time_now) == str(new_time[:-7]):
            user.ip_address['ip'].append(request.META.get('REMOTE_ADDR'))
            user.save()
            return render(request, 'success.html',
                          context={'success': 'Urządzenie zostało potwierdzone'})
        else:
            return render(request, 'error.html',
                          context={'error': 'Niewłaściwy token'})
    

def chack_email(request):
    return render(request, 'logout.html')


def logout_view(request):
    user = get_object_or_404(CustomUser, id=request.user.pk)
    if user.fp_token:
        blacklist_token(user.fp_token)
    logout(request)
    return redirect('login')


class UpdateUser(UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('home')
    template_name = 'update_password.html'


def forgotPassword(request):
    
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            user = CustomUser.objects.get(email=email)
            now = datetime.now()
            forgot_password_mail(email, user)
    except Exception as e:
        print(e)
        return render(request, 'error.html', 
                              context={'error': e})
    return render(request, 'forgot_password.html')


def changePassword(request, token, uidb64):
    token_time = f'{token[36:40]}-{token[76:78]}-{token[114:116]} {token[152:154]}:{token[190:192]}'
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    one_minute = timedelta(minutes=1)
    new_time = str(time_now) + str(one_minute)
    if request.method == 'GET':
        if token_time == str(time_now) or token_time == str(new_time[:-7]):
            print('GET token_time', token_time)
            print('GET time_now', time_now)
            print('GET new_time', new_time[:-7])
        else:
            print('ERROR!!!!!!!!!!!!!!!!!!')
            return render(request, 'error.html', 
                          context={'error': 'Niewłaściwy token'})
    if request.method == 'POST':  
        print('POST token_time', token_time)
        print('POST time_now', time_now)
        print('POST new_time', new_time[:-7])
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_id = urlsafe_base64_decode(uidb64)
        user = CustomUser.objects.get(id=user_id)
        print('Poszło', password1, password2)
        user.set_password(password2)
        user.fp_token = token
        user.save()
        return render(request, 'success_change_password.html', 
               context={'success': 'Hasło zostało zmienione'})

    return render(request, 'change_password.html')
    

def Profile(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    # user = CustomUser.objects.get(id=pk)
    if request.method == 'POST':
        prof_list = [
            'username', 'email', 'birthday', 'workplace', 'religion',
            'insurance_number', 'tax_number', 'adress_pl', 'adress_de',
            'profession', 'position', 'internal_tax_number', 'nfz_name',
            'nfz_adress', 'phone_number', 'bank', 'bic_swift', 'bank_account',
            'health_insurance_de', 'health_insurance_de_number', 'shoe_size',
            'growth', 'work_clothes', 'rights', 'vacations_days_quantity_de',
            'last_year_vacations_days_quantity_de', 'days_to_use_in_current_year_de',
            'acceptation',
        ]

        for field in prof_list:
            if field == 'acceptation':
                value = request.POST.get(field)
                if value == 'Tak':
                    setattr(user, field, True)
                else:
                    setattr(user, field, False)
            else:
                value = request.POST.get(field)
            if value and value != request.POST.get('acceptation'):
                try:
                    setattr(user, field, value)
                except Exception as e:
                    return render(request, 'error.html', {'error': e})
        user.save()
        return redirect('user', pk)
    
    context = {
        'user': user,
    }

    return render(request, 'profile.html', context)


def AllUsers(request):
    users = CustomUser.objects.all()
    users_list = CustomUser.objects.values_list('username', flat=True)
    paginator = Paginator(users, 10) 
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    if request.method == 'POST':
        select = request.POST.get('user')
        if select == 'Wszyscy pracownicy':
            users = CustomUser.objects.all()
        else:
            users = CustomUser.objects.filter(username=select)

    context = {
        'users': users,
        'users_list': users_list,
    }
    return render(request, 'all_users.html', context)


def deleteQuestion(request, pk):
    user = CustomUser.objects.get(id=pk)
    context = {
        'pk': pk,
        'user': user.username,
    }
    return render(request, 'deleteQuestion.html', context)


def deleteUser(request, pk, user):
    u = CustomUser.objects.get(id=pk)
    try:
        u.delete()
        return render(request, 'success_delete_user.html', {'user': u.username})
    except Exception as e:
        error = f'Wystąpił błąd: {e}'
        return render(request, 'error.html', {'error': error})