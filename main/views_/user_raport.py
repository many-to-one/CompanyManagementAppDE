from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from ..tasks import *
from ..models import (
    Work, 
    WorkObject, 
    )
from users.models import CustomUser
from django.core.paginator import Paginator
from django.db.models import Sum


#**********************************************************************************************************************#
#****************************************************** USER RAPORT ***************************************************#
#**********************************************************************************************************************#


def getUserRaport(request, user_pk):
    user = get_object_or_404(CustomUser, id=user_pk)
    work_objects = WorkObject.objects.filter(user__id=user_pk)
    if request.user.is_superuser:
        try:
            works = Work.objects.filter(user=user).order_by('-date')
        except Exception as e:
            error = f'Nie można wyświetlić raport z powodu błędu: {e}'
            return render(request, 'error.html', context=error)
    else:
        try:
            works = Work.objects.filter(user=request.user).order_by('-date')
        except Exception as e:
            error = f'Nie można wyświetlić raport z powodu błędu: {e}'
            return render(request, 'error.html', context=error)
        
    ######################
    ### Totals for all ###

    total_fields = {
        'total_material_costs': 'material_costs',
        'total_coffee_food': 'coffee_food',
        'total_fuel': 'fuel',
        'total_prepayment': 'prepayment',
        'total_phone_costs': 'phone_costs',
        'total_payment': 'payment',
        'total_sum_time_sec': 'sum_time_sec',
        'total_sum_over_time_sec': 'sum_over_time_sec'
    }

    totals = {}
    for field_name, field in total_fields.items():
        total = Work.objects.filter(
            user__id=user_pk
            ).aggregate(
            total=Sum(field)
            )['total']
        totals[field_name] = total

    ### End Totals for all ###
    ##########################

    if request.method == 'POST':
        if 'marked' in request.POST:
            marked = request.POST.getlist('marked')
            request.session['marked'] = marked
            if marked is not None:
                return redirect ('deleteListUserWorkQuestion')
            
        ### Sorted by date 
        sorted_from = request.POST.get('sorted_from')
        work_object = request.POST.get('work_object')

        #####################################################################################
        ###################################  SORTED FROM  ###################################
        #####################################################################################

        if sorted_from:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))
            try:
                # works = Work.objects.filter(
                #     date__range=(start, end),
                #     user__id=user_pk,
                # ).order_by('date')
                works = Work.objects.prefetch_related('user').filter(
                    date__range=(start, end),
                ).order_by('-date')
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context=error)

            # Totals
            totals = {}
            for field_name, field in total_fields.items():
                total = works.aggregate(
                    total=Sum(field)
                    )['total']
                totals[field_name] = total

        
        #####################################################################################
        ###################################  WORK OBJECT  ###################################
        #####################################################################################

        if work_object: 
            wo = get_object_or_404(WorkObject, id=work_object)
            try:
                works = Work.objects.filter(
                    work_object=wo.name,
                    user__id=user_pk,
                    ).order_by('date')
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context=error)
            
            # Totals
            totals = {}
            for field_name, field in total_fields.items():
                total = works.aggregate(
                    total=Sum(field)
                    )['total']
                totals[field_name] = total
        
        #####################################################################################
        ##########################  SORTED FROM & WORK OBJECT  ##############################
        #####################################################################################

        if sorted_from and work_object:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))
            wo = WorkObject.objects.get(id=work_object)
            try:
                works = Work.objects.filter(
                        date__range=(start, end),
                        work_object=wo.name,
                        user__id=user_pk,
                    ).order_by('date')
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context=error)
            
            # Totals
            totals = {}
            for field_name, field in total_fields.items():
                total = works.aggregate(
                    total=Sum(field)
                    )['total']
                totals[field_name] = total

    if totals['total_sum_time_sec']: 
        ### total_sum_time_sec => hours:minutes ###
        total_hours = totals['total_sum_time_sec'] // 3600
        total_sec = totals['total_sum_time_sec'] % 3600
        total_min = total_sec // 60
        total_work_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_time = '0:00'
    if totals['total_sum_over_time_sec']:
        ### total_sum_over_time_sec => hours:minutes ###
        total_hours = totals['total_sum_over_time_sec'] // 3600
        total_sec = totals['total_sum_over_time_sec'] % 3600
        total_min = total_sec // 60
        if total_min < 10 or total_min == 0.0:
            total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
        else:
            total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_over_time = '0:00'

    paginator = Paginator(works, 35)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user': user,
        'works': works,
        'work_objects': work_objects,
        'total_material_costs': totals['total_material_costs'],
        'total_coffee_food': totals['total_coffee_food'],
        'total_fuel': totals['total_fuel'],
        'total_prepayment': totals['total_prepayment'],
        'total_phone_costs': totals['total_phone_costs'],
        'total_payment': totals['total_payment'],
        'total_work_time': total_work_time,
        'total_work_over_time': total_work_over_time,
        'page_obj': page_obj,
    }
    return render(request, 'user_raport.html', context)
