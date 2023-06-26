# from base64 import urlsafe_b64decode
# from typing import Any, Dict
# from django.db import models
# from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
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
    user = CustomUser.objects.get(id=pk)
    if request.method == 'POST':
        username = request.POST.get('username')
        if username is not None:
            user.username = username
            user.save()
            return redirect('user', pk)
        email = request.POST.get('email')
        if email is not None:
            user.email = email
            user.save()
            return redirect('user', pk)
        birthday = request.POST.get('birthday')
        if birthday is not None:
            user.birthday = birthday
            user.save()
            return redirect('user', pk)
        birthplace = request.POST.get('birthplace')
        if birthplace is not None:
            user.birthplace = birthplace
            user.save()
            return redirect('user', pk)
        workplace = request.POST.get('workplace')
        if workplace is not None:
            user.workplace = workplace
            user.save()
            return redirect('user', pk)
        religion = request.POST.get('religion')
        if religion is not None:
            user.religion = religion
            user.save()
            return redirect('user', pk)
        insurance_number = request.POST.get('insurance_number')
        if insurance_number is not None:
            user.insurance_number = insurance_number
            user.save()
            return redirect('user', pk)
        tax_number = request.POST.get('tax_number')
        if tax_number is not None:
            user.tax_number = tax_number
            user.save()
            return redirect('user', pk)
        adress_pl = request.POST.get('adress_pl')
        if adress_pl is not None:
            user.adress_pl = adress_pl
            user.save()
            return redirect('user', pk)
        adress_de = request.POST.get('adress_de')
        if adress_de is not None:
            user.adress_de = adress_de
            user.save()
            return redirect('user', pk)
        profession = request.POST.get('profession')
        if profession is not None:
            user.profession = profession
            user.save()
            return redirect('user', pk)
        position = request.POST.get('position')
        if position is not None:
            user.position = position
            user.save()
            return redirect('user', pk)
        internal_tax_number = request.POST.get('internal_tax_number')
        if internal_tax_number is not None:
            user.internal_tax_number = internal_tax_number
            user.save()
            return redirect('user', pk)
        nfz_name = request.POST.get('nfz_name')
        if nfz_name is not None:
            user.nfz_name = nfz_name
            user.save()
            return redirect('user', pk)
        nfz_adress = request.POST.get('nfz_adress')
        if nfz_adress is not None:
            user.nfz_adress = nfz_adress
            user.save()
            return redirect('user', pk)
        phone_number = request.POST.get('phone_number')
        if phone_number is not None:
            user.phone_number = phone_number
            user.save()
            return redirect('user', pk)
        bank = request.POST.get('bank')
        if bank is not None:
            user.bank = bank
            user.save()
            return redirect('user', pk)
        bic_swift = request.POST.get('bic_swift')
        if bic_swift is not None:
            user.bic_swift = bic_swift
            user.save()
            return redirect('user', pk)
        bank_account = request.POST.get('bank_account')
        if bank_account is not None:
            user.bank_account = bank_account
            user.save()
            return redirect('user', pk)
        health_insurance_de = request.POST.get('health_insurance_de')
        if health_insurance_de is not None:
            user.health_insurance_de = health_insurance_de
            user.save()
            return redirect('user', pk)
        health_insurance_de_number = request.POST.get('health_insurance_de_number')
        if health_insurance_de_number is not None:
            user.health_insurance_de_number = health_insurance_de_number
            user.save()
            return redirect('user', pk)
        shoe_size = request.POST.get('shoe_size')
        if shoe_size is not None:
            user.shoe_size = shoe_size
            user.save()
            return redirect('user', pk)
        growth = request.POST.get('growth')
        if growth is not None:
            user.growth = growth
            user.save()
            return redirect('user', pk)
        work_clothes = request.POST.get('work_clothes')
        if work_clothes is not None:
            user.work_clothes = work_clothes
            user.save()
            return redirect('user', pk)
        rights = request.POST.get('rights')
        if rights is not None:
            user.rights = rights
            user.save()
            return redirect('user', pk)
        vacations_days_quantity_de = request.POST.get('vacations_days_quantity_de')
        if vacations_days_quantity_de is not None:
            user.vacations_days_quantity_de = vacations_days_quantity_de
            user.save()
            return redirect('user', pk)
        last_year_vacations_days_quantity_de = request.POST.get('last_year_vacations_days_quantity_de')
        if last_year_vacations_days_quantity_de is not None:
            user.last_year_vacations_days_quantity_de = last_year_vacations_days_quantity_de
            user.save()
            return redirect('user', pk)
        days_to_use_in_current_year_de = request.POST.get('days_to_use_in_current_year_de')
        if days_to_use_in_current_year_de is not None:
            user.days_to_use_in_current_year_de = days_to_use_in_current_year_de
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
        print('user was deleted', u)
        messages.warning(request, f'Użytkownik {user} został usunięty')
        return redirect('success_delete_user', user)
    except Exception as e:
        print('e', e)
    return redirect('all_users')


def success_delete_user(request, user):
    context = {
        'user': user,
    }
    return render(request, 'success_delete_user.html', context)