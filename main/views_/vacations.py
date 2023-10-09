from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from users.models import CustomUser
from django.core.paginator import Paginator
from datetime import datetime, timedelta, date
import json
from django.urls import reverse
from ..models import VacationRequest, Vacations
from django.http import JsonResponse
from django.contrib import messages


#**********************************************************************************************************************#
#****************************************************** VACATIONS *****************************************************#
#**********************************************************************************************************************#


def addVacation(request):
    user = request.user
    date = datetime.now().strftime('%Y-%m-%d')
    types = [
        'wypoczynkowy',
        'bezpłatny',
    ]
    if request.method == 'POST':
        v_from = request.POST.get('v_from')
        v_to = request.POST.get('v_to')
        type = request.POST.get('type')
        days_planned = request.POST.get('days_planned')
        
        ## Potential mistakes from user
        if int(days_planned) <= 0:
            messages.warning(request, 'Prawdopodobnie została niepoprawnie podana data końcowa')
            return redirect('vacations', user.id)
        if type == 'wypoczynkowy' or type == 'na żądanie':   
            if request.user.days_to_use_in_current_year_de == 0:
                messages.warning(request, 'Nie masz więcej urlopu')
                return redirect('vacations', user.id)
            elif type == 'wypoczynkowy' and int(days_planned) > request.user.days_to_use_in_current_year_de  :
                messages.warning(request, f'Masz do dyspozycji tylko {request.user.days_to_use_in_current_year_de } dni urlopu wypoczynkowego')
                return redirect('vacations', user.id)
            elif type == 'na żądanie' and int(days_planned) > 4 :
                messages.warning(request, 'Urlop na żądanie nie może wynosić więcej niż 4 dni')
                return redirect('vacations', user.id)
            elif type == 'na żądanie' and int(days_planned) > request.user.vacacions_on_demand :
                messages.warning(request, f'Masz do dyspozycji tylko {request.user.vacacions_on_demand} dni urlopu na żądanie')
                return redirect('vacations', user.id)
            elif type == 'na żądanie' and request.user.vacacions_on_demand == 0:
                messages.warning(request, 'Urlop na żądanie został wykorzystany')
                return redirect('vacations', user.id)
        elif type == 'opiekuńczy':
            if int(days_planned) > request.user.cares_vacations:
                messages.warning(request, 'Pozostało mniej dni niż potrzebujesz')
                return redirect('vacations', user.id)
            elif request.user.cares_vacations == 0:
                    messages.warning(request, 'Urlop opiekuńczy został wykorzystany')
                    return redirect('vacations', user.id)
        elif type == 'z powodu siły wyższej':
            if int(days_planned) > request.user.force_majeure_vacations:
                messages.warning(request, 'Liczba dni urlopu musi być odpowiednia do pozostałej')
                return redirect('vacations', user.id)
            elif request.user.force_majeure_vacations == 0:
                messages.warning(request, 'Urlop opiekuńczy został wykorzystany')
                return redirect('vacations', user.id)
        elif type == 'okolicznościowy':
            if int(days_planned) > request.user.compassionate_vacations:
                messages.warning(request, 'Liczba dni urlopu musi być odpowiednia do pozostałej')
                return redirect('vacations', user.id)
        elif not days_planned or int(days_planned) == 0:
             messages.warning(request, 'Nie podałeś ilości dni urlopu')
             return redirect('vacations', user.id)
        elif int(days_planned) > request.user.days_to_use_in_current_year_de  and type != 'bezpłatny':
            messages.warning(request, 'Pozostałych dni urlopu mniej niż potrzebujesz')
            return redirect('vacations', user.id)

        try:
            vacation = Vacations(
            user=request.user,
            username=user.username,
            date=date,
            v_from=v_from,
            v_to=v_to,
            type=type,
            days_planned=days_planned,
            consideration=True,
            )
            vacation.save()
            req = VacationRequest(
                v_request=vacation
            )
            req.save()

            ## Looking for same vacations days
            vacs = Vacations.objects.filter(
                accepted=True,
            )
            requesteded_start_date = datetime.strptime(vacation.v_from, '%Y-%m-%d')
            requesteded_end_date = datetime.strptime(vacation.v_to, '%Y-%m-%d')
            for v in vacs:
                accepted_start_date = datetime.strptime(v.v_from, '%Y-%m-%d')
                accepted_end_date = datetime.strptime(v.v_to, '%Y-%m-%d')
                x_date = accepted_start_date
                while x_date <= accepted_end_date:
                    if x_date == requesteded_start_date or x_date == requesteded_end_date:
                        messages.warning(request, 'Ten termin już zarezerwowany, wybierz inny')
                        vacation.delete()
                        return redirect('addVacation')
                    else:
                        x_date += timedelta(days=1)

            messages.success(request, 'Złożyłeś wniosek o urlop')
            return redirect('vacations', user.id)
        except Exception as e:
            messages.warning(request, f'Błąd: {e}. Nie powiodło się, odśwież stronę i spróbój ponownie')
            return redirect(reverse('vacations', user.id))
    
    context = {
        'date': date,
        'types': types,
    }
    return render(request, 'add_vacation.html', context)


## Editing request if it nos accepted yet (only)
def editVacation(request, pk):
    user = request.user
    vacation = Vacations.objects.get(id=pk)
    date = datetime.now().strftime('%Y-%m-%d')
    types = [
        'wypoczynkowy',
        'bezpłatny',
    ]
    if request.method == 'POST':
        v_from = request.POST.get('v_from')
        v_to = request.POST.get('v_to')
        type = request.POST.get('type')
        days_planned = request.POST.get('days_planned')
        
        ## Potential mistakes from user
        if int(days_planned) <= 0:
            messages.warning(request, 'Prawdopodobnie została niepoprawnie podana data końcowa')
            return redirect('vacations', user.id)
        if type == 'wypoczynkowy' or type == 'na żądanie':   
            if request.user.days_to_use_in_current_year_de == 0:
                messages.warning(request, 'Nie masz więcej urlopu')
                return redirect('vacations', user.id)
            elif int(days_planned) > request.user.days_to_use_in_current_year_de :
                messages.warning(request, f'Masz do dyspozycji tylko {request.user.days_to_use_in_current_year_de } dni urlopu wypoczynkowego')
                return redirect('vacations', user.id)
            elif type == 'na żądanie' and int(days_planned) > 4 :
                messages.warning(request, 'Urlop na żądanie nie może wynosić więcej niż 4 dni')
                return redirect('vacations', user.id)
            elif type == 'na żądanie' and int(days_planned) > request.user.vacacions_on_demand  :
                messages.warning(request, f'Masz do dyspozycji tylko {request.user.vacacions_on_demand } dni urlopu na żądanie')
                return redirect('vacations', user.id)
            elif type == 'na żądanie' and request.user.vacacions_on_demand  == 0:
                messages.warning(request, 'Urlop na żądanie został wykorzystany')
                return redirect('vacations', user.id)
        elif type == 'opiekuńczy':
            if int(days_planned) > request.user.cares_vacations:
                messages.warning(request, 'Pozostało mniej dni niż potrzebujesz')
                return redirect('vacations', user.id)
            elif request.user.cares_vacations == 0:
                    messages.warning(request, 'Urlop opiekuńczy został wykorzystany')
                    return redirect('vacations', user.id)
        elif type == 'z powodu siły wyższej':
            if int(days_planned) > request.user.force_majeure_vacations:
                messages.warning(request, 'Liczba dni urlopu musi być odpowiednia do pozostałej')
                return redirect('vacations', user.id)
            elif request.user.force_majeure_vacations == 0:
                messages.warning(request, 'Urlop opiekuńczy został wykorzystany')
                return redirect('vacations', user.id)
        elif type == 'okolicznościowy':
            if int(days_planned) > request.user.compassionate_vacations:
                messages.warning(request, 'Pozostało mniej dni niż potrzebujesz')
                return redirect('vacations', user.id)
        elif not days_planned or int(days_planned) == 0:
             messages.warning(request, 'Nie podałeś ilości dni urlopu')
             return redirect('vacations', user.id)
        elif int(days_planned) > request.user.days_to_use_in_current_year_de and type != 'bezpłatny' :
            messages.warning(request, 'Pozostałych dni urlopu mniej niż potrzebujesz')
            return redirect('vacations', user.id)
    
        try:
            vacation = Vacations.objects.get(id=pk)
            vacation.date = date
            vacation.v_from = v_from
            vacation.v_to = v_to
            vacation.type = type
            vacation.days_planned = int(days_planned)
            vacation.consideration = True
            vacation.save() 
            return redirect('vacations', user.id)
        except Exception as e:
            messages.warning(request, f'Błąd: {e}. Nie powiodło się, odśwież stronę i spróbój ponownie')
            return redirect(reverse('vacations', user.id))

    context = {
        'vacation': vacation,
        'date': date,
        'types': types,
    }
    return render(request, 'edit_vacation.html', context)


def deleteVacationPage(request, pk):
    vacation = Vacations.objects.get(id=pk)
    context = {
        'vacation': vacation,
        }
    return render(request, 'deleteVacationPage.html', context)


def deleteVacation(request, pk):
    user = request.user
    Vacations.objects.filter(id=pk).delete()
    return redirect('vacations', user.id)


def deleteVacationRequestQuestion(request):
    if request.method == 'GET':
        response = {'message': 'ok',}    
    return JsonResponse(response) 


def deleteVacationRequest(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        req_ids = data.get('req', [])
    try:
        for req_id in req_ids:
            vacation_request = VacationRequest.objects.get(id=req_id)
            vacation_request.delete()
    except Exception as e:
        return render(request, 'error.html', 
                      context={f'Wystąpił błąd:': {e}})
    response = {
        'message': 'ok'
    }
    return JsonResponse(response) 


def allVacationRequests(request):
    reqs = VacationRequest.objects.all().order_by('-v_request__id')
    users = CustomUser.objects.all().values('username')
    types = [
        'wypoczynkowy',
        'bezpłatny',
    ]
    paginator = Paginator(reqs, 10)  

    page_number = request.GET.get('page')
    reqs = paginator.get_page(page_number)

    ## Filter
    if request.method == 'POST':
        sorted_from = request.POST.get('sorted_from')
        sorted_to = request.POST.get('sorted_to')
        user = request.POST.get('user')
        type = request.POST.get('type')
        status = request.POST.get('status')

        #####################################################################################
        ###################################  SORTED FROM  ###################################
        #####################################################################################

        if sorted_from and user and type and status:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day)).date()
            end = datetime(int(year_), int(month_), int(day_)).date()
            if status == 'Zaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__date__range=(start, end),
                    v_request__user__username=user,
                    v_request__type=type,
                    v_request__accepted=True,
                )
            elif status == 'Niezaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__date__range=(start, end),
                    v_request__user__username=user,
                    v_request__type=type,
                    v_request__accepted=False,
                )
            elif status == 'Rozpatrywane':
                reqs = VacationRequest.objects.filter(
                    v_request__date__range=(start, end),
                    v_request__user__username=user,
                    v_request__type=type,
                    v_request__consideration=True,
                )
            print('sorted_from and user and type and status', reqs)
           
        elif sorted_from and user and type:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day)).date()
            end = datetime(int(year_), int(month_), int(day_)).date()
            reqs = VacationRequest.objects.filter(
                v_request__date__range=(start, end),
                v_request__user__username=user,
                v_request__type=type,
            )
            print('sorted_from and user and type', reqs)

        elif sorted_from and user:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day)).date()
            end = datetime(int(year_), int(month_), int(day_)).date()
            reqs = VacationRequest.objects.filter(
                v_request__date__range=(start, end),
                v_request__user__username=user,
            )
            print('sorted_from and user', reqs)

        elif sorted_from and type:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day)).date()
            end = datetime(int(year_), int(month_), int(day_)).date()
            reqs = VacationRequest.objects.filter(
                v_request__date__range=(start, end),
                v_request__type=type,
            )
            print('sorted_from and type', reqs)

        elif sorted_from and status:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day)).date()
            end = datetime(int(year_), int(month_), int(day_)).date()
            if status == 'Zaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__date__range=(start, end),
                    v_request__accepted=True,
                )
            elif status == 'Niezaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__date__range=(start, end),
                    v_request__accepted=False,
                )
            elif status == 'Rozpatrywane':
                reqs = VacationRequest.objects.filter(
                    v_request__date__range=(start, end),
                    v_request__consideration=True,
                )
            print('sorted_from and status', reqs)

        elif sorted_from:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day)).date()
            end = datetime(int(year_), int(month_), int(day_)).date()
            reqs = VacationRequest.objects.filter(
                v_request__date__range=(start, end),
            )
            print('sorted_from', reqs)
        
        elif user and type and status:
            if status == 'Zaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__user__username=user,
                    v_request__type=type,
                    v_request__accepted=True,
                )
            elif status == 'Niezaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__user__username=user,
                    v_request__type=type,
                    v_request__accepted=False,
                )
            elif status == 'Rozpatrywane':
                reqs = VacationRequest.objects.filter(
                    v_request__user__username=user,
                    v_request__type=type,
                    v_request__consideration=True,
                )
            print('user and type and status', reqs)

        elif user and type:
            reqs = VacationRequest.objects.filter(
                v_request__user__username=user,
                v_request__type=type,
            )
            print('user and type', reqs)

        elif user and status:
            if status == 'Zaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__user__username=user,
                    v_request__accepted=True,
                )
            elif status == 'Niezaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__user__username=user,
                    v_request__accepted=False,
                )
            elif status == 'Rozpatrywane':
                reqs = VacationRequest.objects.filter(
                    v_request__user__username=user,
                    v_request__consideration=True,
                )
            print('user and status', reqs)

        elif type and status:
            if status == 'Zaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__type=type,
                    v_request__accepted=True,
                )
            elif status == 'Niezaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__type=type,
                    v_request__accepted=False,
                )
            elif status == 'Rozpatrywane':
                reqs = VacationRequest.objects.filter(
                    v_request__type=type,
                    v_request__consideration=True,
                )
            print('type and status', reqs)

        elif user:
            reqs = VacationRequest.objects.filter(
                v_request__user__username=user,
            )
            print('user', reqs)

        elif type:
            reqs = VacationRequest.objects.filter(
                v_request__type=type,
            )
            print('type', reqs)

        elif status:
            if status == 'Zaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__accepted=True,
                )
            elif status == 'Niezaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__accepted=False,
                )
            elif status == 'Rozpatrywane':
                reqs = VacationRequest.objects.filter(
                    v_request__consideration=True,
                )
            print('status', status)
            
    context = {
       'reqs': reqs, 
       'users': users,
       'types': types,
    }
    return render(request, 'all_vacation_requests.html', context)


def vacationRequest(request, pk):

    req = VacationRequest.objects.filter(
        v_request__id=pk
        ).select_related(
        'v_request'
        ).only(
        'v_request__username', 
        'v_request__type', 
        'v_request__date', 
        'v_request__v_from', 
        'v_request__v_to', 
        'v_request__days_planned'
        ).first()
  
    print('VACATIONREQUEST', req.v_request.days_planned, req)
    vacation = Vacations.objects.get(id=pk)
    type = vacation.type

    ## Days quantity from the first day of the year
    today = date.today()
    start_of_year = date(today.year, 1, 1)
    days_since_start = (today - start_of_year).days

    ## Days of vacations DE actually to use in current year
    current_month = datetime.now().month
    days_to_use = vacation.user.vacations_days_quantity_de / 12 * current_month ###
    vacation.actually_days_to_use = round(days_to_use)

    if request.method == 'POST':
        if 'accept' in request.POST and type in ['wypoczynkowy', 'na żądanie']:
            vacation.accepted = True
            vacation.consideration = False
            if vacation.user.last_year_vacations_days_quantity_de > 0: ###
                if req.v_request.days_planned >= vacation.user.last_year_vacations_days_quantity_de: ###
                    vacation.days_used_in_last_year = vacation.user.vacations_days_quantity_de - vacation.days_to_use_in_last_year ###
                    vacation.days_used_in_current_year = req.v_request.days_planned - vacation.user.last_year_vacations_days_quantity_de ###
                    vacation.days_to_use_in_last_year = 0
                    vacation.user.days_to_use_in_current_year_de = vacation.user.vacations_days_quantity_de - vacation.days_used_in_current_year ###
                    vacation.user.last_year_vacations_days_quantity_de = 0 ###
                else:
                    vacation.user.last_year_vacations_days_quantity_de -=  req.v_request.days_planned ###
                    vacation.days_to_use_in_last_year = vacation.user.last_year_vacations_days_quantity_de  ## Duplicate for Vacations model ###
                    vacation.days_used_in_last_year = vacation.user.vacations_days_quantity_de - vacation.user.last_year_vacations_days_quantity_de ###
                    vacation.days_to_use_in_current_year = vacation.user.vacations_days_quantity - vacation.days_used_in_current_year ###
            else:
                vacation.user.days_to_use_in_current_year_de = vacation.user.days_to_use_in_current_year_de - req.v_request.days_planned
                vacation.days_used_in_current_year = vacation.user.vacations_days_quantity_de - vacation.user.days_to_use_in_current_year_de
                vacation.days_used_in_last_year = vacation.user.vacations_days_quantity_de - vacation.user.last_year_vacations_days_quantity_de
            if today == start_of_year:
                vacation.user.last_year_vacations_days_quantity_de = vacation.days_to_use_in_current_year
                vacation.user.days_to_use_in_current_year_de = vacation.user.vacations_days_quantity_de
            vacation.save()
            vacation.user.save()
            return redirect('allVacationRequests')
        
        
        elif 'accept' in request.POST and type == 'bezpłatny':
            vacation.accepted = True
            vacation.consideration = False
            vacation.save()
            return redirect('allVacationRequests')

        elif 'reject' in request.POST:
            vacation.accepted = False
            vacation.consideration = False
            vacation.save()
            return redirect('allVacationRequests')
    context = {
        'req': vacation,
        'pk': pk,
    }
    return render(request, 'vacation_request.html', context)


def vacations(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    try:
        users = Vacations.objects.all().values('username')
        username_list = [user['username'] for user in users]
        vacations = Vacations.objects.filter(user__id=user.id).order_by('-id')
    except Exception as e:
                error = f'Nie można wyświetlić urlopów z powodu błędu: {e}'
                return render(request, 'error.html', context=error)
    years_list = [vacation.v_from[:4] for vacation in vacations] 
    paginator = Paginator(vacations, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    request.session['users'] = username_list
    all_years = Vacations.objects.all()
    all_years_list = [year.v_from[:4] for year in all_years]
    request.session['years'] = sorted(list(set(all_years_list)))

    ## Days quantity from the first day of the year
    today = date.today()
    start_of_year = date(today.year, 1, 1)
    days_since_start = (today - start_of_year).days

    ## Days of vacations DE actually to use in current year
    current_month = datetime.now().month
    try:
        days_to_use = user.vacations_days_quantity_de / 12 * current_month
        vacations.actually_days_to_use = round(days_to_use)
    except:
        error = 'Twoje dane nie zostały uzupełnione, zwróć się do Administartora.'
        return render(request, 'error.html', {'error': error})

    today = date.today()
    first_day_of_the_year = date(today.year, 1, 1)

    ## Changes quantity of vacations to default when the new year is started
    if today == first_day_of_the_year:
        user.last_year_vacations_days_quantity_de = user.days_to_use_in_current_year_de
        user.days_to_use_in_current_year_de = user.vacations_days_quantity_de
        user.save()

    ## Making a vacation request
    if request.method == 'POST':
        if 'user' in request.POST:
            user_option = request.POST.get('user')
            try:
                user = CustomUser.objects.get(username=user_option)
            except:
                return render(request, 'error.html', {'error': 'Użytkownik nie istnije'})
            return redirect('vacations', user.id)

        elif 'year' in request.POST:
            year = request.POST.get('year')
            if year is not None:
                try:
                    vacations = Vacations.objects.filter(
                        user__id=request.user.id,
                        v_from__startswith=year,
                        ).order_by('-id')
                except Exception as e:
                    error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                    return render(request, 'error.html', context=error)
        elif 'marked' in request.POST:
            marked = request.POST.getlist('marked')
            if marked is not None:
                request.session['marked'] = marked # Here we need to send this list to the delete_vacations_requests function
                return redirect('delete_vacations_question')

    context = {
        'vacations': vacations,
        'user': user,
        'users': set(username_list),
        'actually_days_to_use': vacations.actually_days_to_use,
        'years_list': set(years_list),
        'days_used_in_current_year': user.vacations_days_quantity_de - user.days_to_use_in_current_year_de,
        'last_year_vacations_used_days_quantity': user.vacations_days_quantity_de - user.last_year_vacations_days_quantity_de,
        'page_obj': page_obj,
    }
    return render(request, 'vacations.html', context)

def delete_vacations_question(request):
    return render(request, 'delete_vacations_question.html')


def delete_vacations(request):
    marked = request.session.get('marked') # Here we get this list from vacations marked form
    pk = request.user.pk
    markeds = Vacations.objects.filter(
                    id__in=marked
                )
    if markeds:
        for marked in markeds:
            marked.delete()
        return redirect('vacations', pk)
    context = {
        'pk': pk
    }
    return render(request, 'delete_vacations_question.html', context)


def vacationsExcelPage(request):
    users = request.session.get('users')
    years = request.session.get('years')

    if request.method == 'POST':
        user = request.POST.get('user')
        year = request.POST.get('year')
        request.session['user'] = user
        request.session['year'] = year
        print('user', user)
        print('year', year)
        return redirect('vacationsToExcel')
    context = {
        'users': users,
        'years': years,
    }
    return render(request, 'vacationsExcelPage.html', context)