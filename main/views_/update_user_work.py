from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from ..tasks import *
from ..models import (
    Work, 
    WorkObject, 
    WorkType, 
    )
from django.contrib import messages
from users.models import CustomUser


#**********************************************************************************************************************#
#************************************************** UPDATE USER WORK **************************************************#
#**********************************************************************************************************************#

def updateUserWork(request, work_pk):
    print('work_pk----------------', work_pk)
    work = Work.objects.prefetch_related('user').filter(id=work_pk).first()
    user = ''
    if work:
        users = work.user.all()
        for us in users:
            user = us
    user = CustomUser.objects.get(id=user.id)

    if request.method == 'POST':
        date = request.POST.get('date')
        timestart = request.POST.get('timestart')
        timefinish = request.POST.get('timefinish')
        timestart_break1 = request.POST.get('timestart_break1')
        timefinish_break1 = request.POST.get('timefinish_break1')
        timestart_break2 = request.POST.get('timestart_break2')
        timefinish_break2 = request.POST.get('timefinish_break2')
        work_object = request.POST.get('work_object')
        work_type = request.POST.get('work_type')
        material_costs = request.POST.get('material_costs')
        coffee_food = request.POST.get('coffee_food')
        fuel = request.POST.get('fuel')
        prepayment = request.POST.get('prepayment')
        phone_costs = request.POST.get('phone_costs')


        if date == '':
            messages.warning(request, 'Wybierz date!')
            return redirect(reverse('update_user_work', kwargs={'work_pk': work_pk}))
        if timestart == '':
            messages.warning(request, 'Zaznacz początek czasu pracy!')
            return redirect(reverse('update_user_work', kwargs={'work_pk': work_pk}))
        if timefinish == '':
            messages.warning(request, 'Zaznacz koniec czasu pracy!')
            return redirect(reverse('update_user_work', kwargs={'work_pk': work_pk}))
        if work_object == None:
            messages.warning(request, 'Wybierz Obiekt pracy!')
            return redirect(reverse('update_user_work', kwargs={'work_pk': work_pk}))

        ### Here we need to make str(date) => int(date) to sum it ###
        year, month, day = date.split('-')
        start_hr, start_min = timestart.split(':') 
        finish_hr, finish_min = timefinish.split(':') 
        start = datetime(int(year), int(month), int(day), int(start_hr), int(start_min))
        end = datetime(int(year), int(month), int(day), int(finish_hr), int(finish_min))

        #BREAKFAST
        if timestart_break1 and timefinish_break1:
            start_hr_break1, start_min_break1 = timestart_break1.split(':')  
            finish_hr_break1, finish_min_break1 = timefinish_break1.split(':') 
            start_break1 = datetime(int(year), int(month), int(day), int(start_hr_break1), int(start_min_break1))
            end_break1 = datetime(int(year), int(month), int(day), int(finish_hr_break1), int(finish_min_break1))
            dif_break1 = end_break1 - start_break1 

            dif_hours_break1 = dif_break1.seconds // 3600
            dif_sec_break1 = dif_break1.seconds % 3600
            dif_min_break1 = dif_sec_break1 // 60
            if dif_min_break1 < 10 or dif_min_break1 == 0:
                bt = f'{dif_hours_break1}:0{dif_min_break1}'
            else:
                bt = f'{dif_hours_break1}:{dif_min_break1}'

            # Work time in seconds without break
            diff = end - start - dif_break1 

        #LANCH
        elif timestart_break2 and timefinish_break2:
            start_hr_break2, start_min_break2 = timestart_break2.split(':')  
            finish_hr_break2, finish_min_break2 = timefinish_break2.split(':') 
            start_break2 = datetime(int(year), int(month), int(day), int(start_hr_break2), int(start_min_break2))
            end_break2 = datetime(int(year), int(month), int(day), int(finish_hr_break2), int(finish_min_break2))
            dif_break2 = end_break2 - start_break2

            dif_hours_break2 = dif_break2.seconds // 3600
            dif_sec_break2 = dif_break2.seconds % 3600
            dif_min_break2 = dif_sec_break2 // 60
            if dif_min_break2 < 10 or dif_min_break2 == 0:
                bt = f'{dif_hours_break2}:0{dif_min_break2}'
            else:
                bt = f'{dif_hours_break2}:{dif_min_break2}'

            # Work time in seconds without break
            diff = end - start - dif_break2

        elif timestart_break1 and timefinish_break1 and timestart_break2 and timefinish_break2:
            start_hr_break1, start_min_break1 = timestart_break1.split(':')  
            finish_hr_break1, finish_min_break1 = timefinish_break1.split(':') 
            start_break1 = datetime(int(year), int(month), int(day), int(start_hr_break1), int(start_min_break1))
            end_break1 = datetime(int(year), int(month), int(day), int(finish_hr_break1), int(finish_min_break1))
            dif_break1 = end_break1 - start_break1 
            start_hr_break2, start_min_break2 = timestart_break2.split(':')  
            finish_hr_break2, finish_min_break2 = timefinish_break2.split(':') 
            start_break2 = datetime(int(year), int(month), int(day), int(start_hr_break2), int(start_min_break2))
            end_break2 = datetime(int(year), int(month), int(day), int(finish_hr_break2), int(finish_min_break2))
            dif_break2 = end_break2 - start_break2

            dif_hours_break2 = dif_break1.seconds // 3600
            dif_sec_break1 = dif_break1.seconds % 3600
            dif_min_break1 = dif_sec_break1 // 60
            if dif_min_break1 < 10 or dif_min_break1 == 0:
                bt = f'{dif_hours_break1}:0{dif_min_break1}'
            else:
                bt = f'{dif_hours_break1}:{dif_min_break1}'

            # Work time in seconds without break
            diff = end - start - dif_break1 - dif_break2

        else:
            # Work time in seconds without break
            diff = end - start 
        
        ### Overtime/day ###
        if diff.seconds > 28800:
            over_time = diff.seconds - 28800
            over_hours = over_time // 3600
            over_sec = diff.seconds % 3600
            over_min = over_sec // 60
            if over_min < 10 or over_min == 0:
                ot = f'{over_hours}:0{over_min}'
            else:
                ot = f'{over_hours}:{over_min}'
            ### To calculate only 8:00 hours###
            # dif_hours = 28800 // 3600       #
            # dif_sec = 28800 % 3600          #
            # dif_min = dif_sec // 60         #
            ###################################
            dif_hours = diff.seconds // 3600
            dif_sec = diff.seconds % 3600
            dif_min = dif_sec // 60

            if dif_min < 10 or dif_min == 0:
                wt = f'{dif_hours}:0{dif_min}'
            else:
                wt = f'{dif_hours}:{dif_min}'
            print('wt', wt)

        ### if overtime/day is "0" ###
        else:
            ot = '00.00'
            over_time = '00.00'
            dif_hours = diff.seconds // 3600
            dif_sec = diff.seconds % 3600
            dif_min = dif_sec // 60
            if dif_min < 10 or dif_min == 0:
                wt = f'{dif_hours}:0{dif_min}'
            else:
                wt = f'{dif_hours}:{dif_min}'

        # work_object = request.POST.get('work_object')
        # work_type = request.POST.get('work_type')
        # coffee_food = request.POST.get('coffee_food')
        # fuel = request.POST.get('fuel')
        # prepayment = request.POST.get('prepayment')
        # phone_costs = request.POST.get('phone_costs')
        try:
            work.date = date
            work.timestart = timestart
            work.timefinish = timefinish
            work.diff_time = wt 
            work.over_time = ot
            #############################################
            ### For calculation time without overtime ###
            # if diff.seconds > 28800:                  #
            #     work.sum_time_sec = 28800             #
            # else:                                     #
            #     work.sum_time_sec = diff.seconds      #
            #############################################
            work.sum_time_sec = diff.seconds
            work.sum_over_time_sec = over_time
            work.work_object = work_object
            work.work_type = work_type
            # if material_costs:
            work.material_costs = float(material_costs)
            work.coffee_food = coffee_food
            work.prepayment = prepayment
            work.fuel = fuel
            work.phone_costs = phone_costs
            work.payment = (user.payment / 3600) * diff.seconds      
            work.timestart_break1 = timestart_break1
            work.timefinish_break1 = timefinish_break1
            work.timestart_break2 = timestart_break2
            work.timefinish_break2 = timefinish_break2 
            work.save()
        except Exception as e:
            error = f'Wystąpił błąd: {e}'
            return render(request, 'error.html', context=error)
        return redirect('raports')
    else:
        work_objects = WorkObject.objects.filter(user__id=user.id)
        work_type = WorkType.objects.all()

    context = {
        'work': work,
        'work_objects': work_objects,
        'work_type': work_type,
        }
    return render(request, 'update_user_work.html', context)
