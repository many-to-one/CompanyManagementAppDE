from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from ..tasks import *
from ..models import (
    Work, 
    WorkObject, 
    )
from django.contrib import messages
from users.models import CustomUser


#**********************************************************************************************************************#
#************************************************* USER CREATE HIS WORK ***********************************************#
#**********************************************************************************************************************#

def userWork(request, pk):
    print('PAYMENT ------------------- ', request.user.payment)
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
            return redirect(reverse('user_work', kwargs={'pk': pk}))
        if timestart == '':
            messages.warning(request, 'Zaznacz początek czasu pracy!')
            return redirect(reverse('user_work', kwargs={'pk': pk}))
        if timefinish == '':
            messages.warning(request, 'Zaznacz koniec czasu pracy!')
            return redirect(reverse('user_work', kwargs={'pk': pk}))
        if work_object == None:
            messages.warning(request, 'Wybierz Obiekt pracy!')
            return redirect(reverse('user_work', kwargs={'pk': pk}))

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
            # print('dif_break1 -------------- ', diff)

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
            # print('dif_break2 --------------', diff)

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
            # print('dif_break1 + dif_break2 --------------', diff)

        else:
            # Work time in seconds without break
            diff = end - start 
            # print('without brak --------------', diff)

        # print('diff_diff --------------', diff)
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

        user = CustomUser.objects.get(id=pk)
        # work_object = WorkObject.objects.get(name=work_object)
        payment = (user.payment / 3600) * diff.seconds
        print('PAYMENT', payment, type(payment))
        try:
            work = Work.objects.create()
            work.date = date
            work.username = user.username
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
            work.material_costs = float(material_costs)
            work.coffee_food = float(coffee_food)
            work.prepayment = float(prepayment)
            work.fuel = float(fuel)
            work.phone_costs = float(phone_costs)
            payment_ = float(payment)
            work.payment = round(payment_, 2)
            if timestart_break1:
                work.timestart_break1 = timestart_break1
            if timefinish_break1:    
                work.timefinish_break1 = timefinish_break1
            if timestart_break2:
                work.timestart_break2 = timestart_break2
            if timefinish_break2:
                work.timefinish_break2 = timefinish_break2
            work.user.add(user)
            try:
                work.save()
            except Exception as e:
                error = f'Nie można zaraportować pracę z powodu błędu: {e}'
                return render(request, 'error.html',
                              context={'error': error})
            return redirect('raports')
        except Exception as e:
            error = f'Nie można zaraportować pracę z powodu błędu: {e}'
            return render(request, 'error.html',
                          context={'error': error})

    work_objects = WorkObject.objects.filter(user__id=pk).only('name')
    return render(request, 'user_work.html',
                  context={'work_objects': work_objects})