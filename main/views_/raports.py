from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from ..tasks import *
from ..models import (
    Work, 
    WorkObject, 
    )
from django.db.models import Prefetch
from users.models import CustomUser
from django.core.paginator import Paginator


#**********************************************************************************************************************#
#****************************************************** ALL RAPORTS ***************************************************#
#**********************************************************************************************************************#


from django.shortcuts import render


def raports(request):

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
    
    if request.user.is_superuser:
        try:
            # works_result = raports_all_superuser.delay() 
            # works = works_result.get()
            # print('WORKS!!!!!!!', works)
            works = Work.objects.prefetch_related(
                Prefetch('user')
                ).order_by('-date')
            # Convert Decimal values to float using dictionary comprehension
            works_dict = [work.__dict__ for work in works]
            works = [
                {key: float(value) if isinstance(value, Decimal) 
                 else value for key, value in work.items() 
                 if key != '_state' and key != '_prefetched_objects_cache'} 
                 for work in works_dict
                ]
            work_objects = WorkObject.objects.all().only('name')

        except Exception as e:
            error = f'Nie można wyświetlić raport z powodu błędu: {e}'
            return render(request, 'error.html', context={'error': error})
    else:
        try:
            # works_result = raports_all.delay(request.user.id)
            # works = works_result.get()
            works = Work.objects.prefetch_related(
                Prefetch('user')
                ).filter(
                user__id=request.user.id
                ).order_by('-date')
            # Convert Decimal values to float using dictionary comprehension
            works_dict = [work.__dict__ for work in works]
            works = [
                {key: float(value) if isinstance(value, Decimal) 
                 else value for key, value in work.items() 
                 if key != '_state' and key != '_prefetched_objects_cache'} 
                 for work in works_dict
                ]
            work_objects = WorkObject.objects.filter(user=request.user).only('name')
        except Exception as e:
            error = f'Nie można wyświetlić raport z powodu błędu: {e}'
            return render(request, 'error.html', context={'error': error})
        
    users = CustomUser.objects.all().values('id', 'username')
        
    # Totals without filters
    totals = {}
    if works:
        for field_name, field in total_fields.items():
            # total = works.aggregate(total=Sum(F(field)))['total']
            total = sum(work[field] for work in works)
            totals[field_name] = round(total, 2)
    else:
        for field_name, field in total_fields.items():
            totals[field_name] = 0.00

    # Filters
    if request.method == 'POST':

        if 'marked' in request.POST:
            marked = request.POST.getlist('marked')
            request.session['marked'] = marked
            if marked is not None:
                return redirect ('deleteListUserWorkQuestion')

        sorted_from = request.POST.get('sorted_from')
        user = request.POST.get('user')
        work_object = request.POST.get('work_object')

        #####################################################################################
        #######################################  ALL  #######################################
        #####################################################################################

        # if sorted_from and user and work_object == '':
        #     try:
        #         works = Work.objects.all().order_by('-date')
        #         # Convert Decimal values to float using dictionary comprehension
        #         works_dict = [work.__dict__ for work in works]
        #         works = [
        #             {key: float(value) if isinstance(value, Decimal) 
        #              else value for key, value in work.items() 
        #              if key != '_state'} 
        #              for work in works_dict
        #             ]
        #     except Exception as e:
        #         error = f'Nie można wyświetlić raport z powodu błędu: {e}'
        #         return render(request, 'error.html', context=error)
        #     ### Making the excel file of raports ###
        #     if user == '' and work_object == '' and sorted_from == '':
        #         filterRaport = request.POST.get('filterRaport')
        #         if filterRaport == 'download':
        #             request.session['works'] = list(works)
        #             return redirect('raportsToExcel')
            
        #     # Totals 
        #     totals = {}
        #     for field_name, field in total_fields.items():
        #         total = works.aggregate(total=Sum(field))['total']
        #         totals[field_name] = round(total, 2)

        #####################################################################################
        ###################################  SORTED FROM  ###################################
        #####################################################################################

        if sorted_from:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))

            # Call task from task.py
            try:
                # works_task = raports_sorted_from.delay(start, end)
                # works = works_task.get()
                works = Work.objects.prefetch_related('user').filter(
                        date__range=(start, end),
                    ).order_by('-date')
                # Convert Decimal values to float using dictionary comprehension
                works_dict = [work.__dict__ for work in works]
                works = [
                    {key: float(value) if isinstance(value, Decimal) 
                     else value for key, value in work.items() 
                     if key != '_state' and key != '_prefetched_objects_cache'} 
                     for work in works_dict
                    ]
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})

            ### Making the excel file of raports ###
            if user == '' and work_object == '':
                filterRaport = request.POST.get('filterRaport')
                if filterRaport == 'download':
                    request.session['works'] = list(works)
                    return redirect('raportsToExcel')
            
            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                # total = works.aggregate(total=Sum(field))['total']
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)


        #####################################################################################
        #######################################  USER  ######################################
        #####################################################################################

        if user:
            # Call task from task.py
            try:
                # works_result = raports_user.delay(user)
                # works = works_result.get()
                works = Work.objects.filter(username=user).order_by('-date')
                # Convert Decimal values to float using dictionary comprehension
                works_dict = [work.__dict__ for work in works]
                works = [
                    {key: float(value) if isinstance(value, Decimal) 
                     else value for key, value in work.items() 
                     if key != '_state'} 
                     for work in works_dict
                    ]
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})
            if sorted_from == '' and work_object == '':
                ### Making the excel file of raports ###
                try:
                    filterRaport = request.POST.get('filterRaport')
                except Exception as e:
                    error = f'Wystąpił błąd: {e}'
                    return render(request, 'error.html', context={'error': error})
                if filterRaport == 'download':
                    try:
                        request.session['works'] = list(works)
                    except Exception as e:
                        error = f'Nie można pobrać raportu z powodu błędu: {e}'
                        return render(request, 'error.html', context={'error': error})
                    return redirect('raportsToExcel')
            
            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                # total = works.aggregate(total=Sum(field))['total']
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)


        #####################################################################################
        ###################################  WORK OBJECT  ###################################
        #####################################################################################

        if work_object: 
            # Call task from task.py
            try:
                # works_result = raports_work_object.delay(work_object)
                # works = works_result.get()
                wo = get_object_or_404(WorkObject, id=work_object)
                works = Work.objects.filter(work_object=wo.name).order_by('-date')
                # Convert Decimal values to float using dictionary comprehension
                works_dict = [work.__dict__ for work in works]
                works = [
                    {key: float(value) if isinstance(value, Decimal) 
                     else value for key, value in work.items() 
                     if key != '_state'} 
                     for work in works_dict
                    ]
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})
            if sorted_from == '' and user == '':
                ### Making the excel file of raports ###
                filterRaport = request.POST.get('filterRaport')
                if filterRaport == 'download':
                    request.session['works'] = list(works)
                    return redirect('raportsToExcel')
            
            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                # total = works.aggregate(total=Sum(field))['total']
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)


        #####################################################################################
        ##########################  SORTED FROM & WORK OBJECT  ##############################
        #####################################################################################

        if sorted_from and work_object:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))

            # Call task from task.py
            try:
                # works_result = raports_sorted_from_work_object.delay(start, end, work_object)
                # works = works_result.get()
                wo = get_object_or_404(WorkObject, id=work_object)
                works = Work.objects.filter(
                    date__range=(start, end),
                    work_object=wo.name,
                ).order_by('-date')
                # Convert Decimal values to float using dictionary comprehension
                works_dict = [work.__dict__ for work in works]
                works = [
                    {key: float(value) if isinstance(value, Decimal) 
                     else value for key, value in work.items() 
                     if key != '_state'} 
                     for work in works_dict
                    ]
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})
            if user == '':
                ### Making the excel file of raports ###
                filterRaport = request.POST.get('filterRaport')
                if filterRaport == 'download':
                    request.session['works'] = list(works)
                    return redirect('raportsToExcel')
            

            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)


        #####################################################################################
        #################################  SORTED FROM & USER  ##############################
        #####################################################################################

        if sorted_from and user:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))

            # Call task from task.py
            try:
                # works_result = raports_sorted_from_user.delay(start, end, user)
                # works = works_result.get()
                works = Work.objects.filter(
                    date__range=(start, end),
                    username=user,
                ).order_by('-date')
                # Convert Decimal values to float using dictionary comprehension
                works_dict = [work.__dict__ for work in works]
                works = [
                    {key: float(value) if isinstance(value, Decimal) 
                     else value for key, value in work.items() 
                     if key != '_state'} 
                     for work in works_dict
                    ]
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})
            if work_object == '':
                ### Making the excel file of raports ###
                filterRaport = request.POST.get('filterRaport')
                if filterRaport == 'download':
                    request.session['works'] = list(works)
                    return redirect('raportsToExcel')

            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)


        #####################################################################################
        #################################  WORK OBJECT & USER  ##############################
        #####################################################################################

        if work_object and user:

            # Call task from task.py
            try:
                # works_result = raports_work_object_user.delay(work_object, user)
                # works = works_result.get()
                wo = get_object_or_404(WorkObject, id=work_object)
                works = Work.objects.filter(
                    work_object=wo.name,
                    username=user
                    ).order_by('-date')
                # Convert Decimal values to float using dictionary comprehension
                works_dict = [work.__dict__ for work in works]
                works = [
                    {key: float(value) if isinstance(value, Decimal) 
                     else value for key, value in work.items() 
                     if key != '_state'} 
                     for work in works_dict
                    ]
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})
            if sorted_from == '':
                ### Making the excel file of raports ###
                filterRaport = request.POST.get('filterRaport')
                if filterRaport == 'download':
                    request.session['works'] = list(works)
                    return redirect('raportsToExcel')

            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)


        #####################################################################################
        ##########################  SORTED FROM & WORK OBJECT & USER  #######################
        #####################################################################################  

        if sorted_from and user and work_object:

            # Call task from task.py
            try:
                # works_result = raports_sorted_from_work_object_user.delay(start, end, work_object, user)
                # works = works_result.get()
                wo = get_object_or_404(WorkObject, id=work_object)
                works = Work.objects.filter(
                    date__range=(start, end),
                    work_object=wo.name,
                    username=user,
                ).order_by('-date')
                # Convert Decimal values to float using dictionary comprehension
                works_dict = [work.__dict__ for work in works]
                works = [
                    {key: float(value) if isinstance(value, Decimal) 
                     else value for key, value in work.items() 
                     if key != '_state'} 
                     for work in works_dict
                    ]
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})
            ### Making the excel file of raports ###
            filterRaport = request.POST.get('filterRaport')
            if filterRaport == 'download':
                request.session['works'] = list(works)
                return redirect('raportsToExcel')
            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)
    
    if totals:
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

    ## List of users, even if the someone has been deleted can be find in raports
    works = Work.objects.values_list('username')
    users_list = set()
    users_list = {wo[0] for wo in works}

    total_lists = [
        totals['total_payment'],
        totals['total_phone_costs'],
        totals['total_fuel'],
        totals['total_material_costs'],
        totals['total_coffee_food'],
        totals['total_material_costs'],
    ]

    if any(element is not None for element in total_lists):
        total = sum(total_lists)
    else:
        total = '0:00'
        totals['total_payment'] = '0:00'
        totals['total_prepayment'] = '0:00'
        totals['total_phone_costs'] = '0:00'
        totals['total_fuel'] = '0:00'
        totals['total_coffee_food'] = '0:00'
        totals['total_material_costs'] = '0.00'

    context = {
        'works': works,
        'users': users, 
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
        'users_list': users_list,
        'total': total,
    }
    return render(request, 'raports.html', context)