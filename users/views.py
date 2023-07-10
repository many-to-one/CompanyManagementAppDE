# from base64 import urlsafe_b64decode
# from typing import Any, Dict
# from django.db import models
# from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, ListView 
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
import datetime
from .utils import forgot_password_mail
from .forms import CustomUserChangeForm, CustomUserCreationForm, \
                   AuthenticationForm, ForgotPassword
from .models import CustomUser
from django.core.paginator import Paginator


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
    
    def form_invalid(self, form):
        messages.error(self.request,'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))
    

def logout_view(request):
    logout(request)
    messages.success(request, 'Log out')
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
    

def Profile(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    if request.method == 'POST':
        prof_list = [
            'username', 'email', 'birthday', 'workplace', 'religion',
            'insurance_number', 'tax_number', 'adress_pl', 'adress_de',
            'profession', 'position', 'internal_tax_number', 'nfz_name',
            'nfz_adress', 'phone_number', 'bank', 'bic_swift', 'bank_account',
            'health_insurance_de', 'health_insurance_de_number', 'shoe_size',
            'growth', 'work_clothes', 'rights', 'vacations_days_quantity_de',
            'last_year_vacations_days_quantity_de', 'days_to_use_in_current_year_de'
        ]

        for field in prof_list:
            value = request.POST.get(field)
            if value:
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