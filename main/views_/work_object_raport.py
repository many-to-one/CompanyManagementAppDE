from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.db.models import Sum
from ..models import Work, WorkObject


#**********************************************************************************************************************#
#*************************************************** WORK OBJECT RAPORT ***********************************************#
#**********************************************************************************************************************#


def workObjectRaport(request, user_pk, object_pk):

    total_fields = {
                'total_coffee_food': 'coffee_food',
                'total_fuel': 'fuel',
                'total_prepayment': 'prepayment',
                'total_phone_costs': 'phone_costs',
                'total_payment': 'payment',
                'total_sum_time_sec': 'sum_time_sec',
                'total_sum_over_time_sec': 'sum_over_time_sec'
            }

    ### Sorted by workobject ###
    work_object = get_object_or_404(WorkObject, id=object_pk)

    ### Sorted by date continue.. ###
    try:
        work_by_date = Work.objects.filter(
            user__id=user_pk,
            work_object=work_object.name,
        ).order_by('date')
    except Exception as e:
        error = f'Nie można wyświetlić raport z powodu błędu: {e}'
        return render(request, 'error.html', context=error)

    # Totals
    totals = {}
    for field_name, field in total_fields.items():
        total = work_by_date.aggregate(total=Sum(field))['total']
        if total:
            totals[field_name] = round(total, 2)
        else:
            totals[field_name] = 0.00
    
    if request.method == 'POST':

        ### Sorted by date ###
        sorted_from = request.POST.get('sorted_from')
        ##############################################
        ##############################################
        if sorted_from:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))
            ### Sorted by date pause.. ###

            ### Sorted by workobject ###
            work_object = get_object_or_404(WorkObject, id=object_pk)

            ### Sorted by date continue.. ###
            try:
                work_by_date = Work.objects.filter(
                    user__id=user_pk,
                    date__range=(start, end),
                    work_object=work_object.name,
                ).order_by('date')
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context=error)

            # Totals
            totals = {}
            for field_name, field in total_fields.items():
                total = work_by_date.aggregate(total=Sum(field))['total']
                totals[field_name] = total

    ## Open page without filtering
    # if totals['total_coffee_food'] is None and \
    #    totals['total_prepayment'] is None and \
    #    totals['total_fuel'] is None and \
    #    totals['total_phone_costs'] is None and \
    #    totals['total_payment'] is None:
    #     totals['total_coffee_food'] = 0.00
    #     totals['total_prepayment'] = 0.00
    #     totals['total_fuel'] = 0.00
    #     totals['total_phone_costs'] = 0.00
    #     totals['total_payment'] = 0.00
    
    total_lists = [
        totals['total_payment'],
        totals['total_phone_costs'],
        totals['total_fuel'],
        totals['total_coffee_food']
    ]

    if any(element is not None for element in total_lists):
        total = sum(total_lists)
    else:
        total = '0:00'
        totals['total_payment'] = '0:00'
        totals['total_prepayment'] = '0:00'
        totals['total_phone_costs'] = '0:01'
        totals['total_fuel'] = '0:00'
        totals['total_coffee_food'] = '0:00'

    ### End Totals for choice ###
    #############################
    
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

    context = {
        'work_by_date': work_by_date,
        'work_object': work_object,
        'total_coffee_food': totals['total_coffee_food'],
        'total_fuel': totals['total_fuel'],
        'total_prepayment': totals['total_prepayment'],
        'total_phone_costs': totals['total_phone_costs'],
        'total_payment': totals['total_payment'],
        'total_work_time': total_work_time,
        'total_work_over_time': total_work_over_time,
    }
    return render(request, 'workobject_raport.html', context)