from datetime import datetime
from django.shortcuts import render, get_object_or_404
from ..tasks import *
from ..models import (
    Work, 
    WorkObject, 
    Message, 
    Subcontractor,
    )
from django.db.models import Sum
from users.models import CustomUser


#**********************************************************************************************************************#
#*************************************************** WORK OBJECT VIEW *************************************************#
#**********************************************************************************************************************#

def workObjectView(request, **kwargs):

    allusers = CustomUser.objects.all()
    work_object = WorkObject.objects.get(id=kwargs['pk'])
    users = work_object.user.all()
    messages = Message.objects.filter(
        work_object=work_object,
       )

    subcontractors = work_object.subcontractor.all()
    subcontractors_sum = Subcontractor.objects.filter(
       work_object=work_object 
    ).aggregate(
        subcontractors_sum=Sum('sum')
    )
    print('work_object.id --------------------', work_object.id)
    print('work_object.name --------------------', work_object.name)
    print('work_object.total --------------------', work_object.total)

    ##############################
    ### Totals for work_object ###

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
            work_object=work_object.id
            ).aggregate(
            total=Sum(field)
            )['total']
        totals[field_name] = total

    # Calculate total work time in this object
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
    ### End Totals for sorted_from ###
    ################################## 
    
    ## Add new user to the object & make chat with all users belong to it
    if request.method == 'POST':
        ## Add new user in work object
        if 'add_user' in request.POST:
            user = request.POST.get('user')
            if user == '':
                error = 'Nie wybrano żadnego użytkownika'
                return render(request, 'error.html', {'error': error})
            # add_user = CustomUser.objects.get(username=user)
            add_user = get_object_or_404(CustomUser, username=user)
            try:
                work_object.user.add(add_user)
                work_object.save()
            except Exception as e:
                return render(request, 
                              'error.html',
                              context={'error': f'Wystąpił błąd: użytkownika nie istnieje, {e}'}
                              )
            work_object = get_object_or_404(WorkObject, id=kwargs['pk'])
            users = work_object.user.all()

    total_lists = [
        totals['total_payment'],
        totals['total_phone_costs'],
        totals['total_fuel'],
        totals['total_coffee_food'],
        totals['total_material_costs'],
    ]

    if any(element is not None for element in total_lists):
        total = sum(total_lists)
    else:
        total = '0.00'
        totals['total_payment'] = '0.00'
        totals['total_prepayment'] = '0.00'
        totals['total_phone_costs'] = '0.00'
        totals['total_fuel'] = '0.00'
        totals['total_coffee_food'] = '0.00'
        totals['total_material_costs'] = '0.00'
    
    sub_sum = subcontractors.aggregate(total=Sum('sum'))['total']
    if sub_sum:
        work_object.total = sub_sum + float(total)
        work_object.save()
    else:
        work_object.total = float(total)
        work_object.save()

    context = {
        'current_time': datetime.now().strftime('%Y-%m-%d'),
        'messages': messages,
        'work_object': work_object,
        'users': users,
        'allusers': allusers,
        'total_material_costs': totals['total_material_costs'],
        'total_coffee_food': totals['total_coffee_food'],
        'total_fuel': totals['total_fuel'],
        'total_prepayment': totals['total_prepayment'],
        'total_phone_costs': totals['total_phone_costs'],
        'total_payment': totals['total_payment'],
        'total_work_time': total_work_time,
        'total': total,
        'subcontractors': subcontractors,
        'subcontractors_sum': subcontractors_sum['subcontractors_sum'],
    }
    return render(request, 'work_object.html', context)


def deleteUserFromObjectQuestion(request, user_pk, work_object_pk):
    try:
        user_query = CustomUser.objects.filter(id=user_pk).values_list('username')
        user = [user[0] for user in user_query]
    except Exception as e:
            return render(request,
                          'error.html',
                          context={'error': f'Wystąpił błąd: {e}'})
    context = {
        'user': user[0],
        'user_pk': user_pk,
        'work_object_pk': work_object_pk
    }
    return render (request, 'deleteUserFromObjectQuestion.html', context)


def deleteUserFromObject(request, user_pk, work_object_pk):
    user = get_object_or_404(CustomUser, id=user_pk)
    work_object = get_object_or_404(WorkObject, id=work_object_pk)
    try:
        work_object.user.remove(user)
        work_object.save()
        context = {
        'username': user.username,
        'work_object': work_object,
        }
        return render(request, 'success_delete_user_from_workobject.html', context)
    except Exception as e:
        error = f'Wystąpił błąd: {e}'
        return render(request, 'error.html', {'error': error})