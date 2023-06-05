from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from .forms import WorkobjectForm
from .models import Work, WorkObject, WorkType, TotalWorkObject, Message
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from datetime import datetime
from django.db.models import F
from django.contrib.auth.decorators import login_required

from users.models import CustomUser
def index(request):
    return render(request, "home.html")


#**********************************************************************************************************************#
#*************************************************** ALL WORK OBJECTS *************************************************#
#**********************************************************************************************************************#


class WorkObjects(ListView):
    model = WorkObject
    template_name = 'work_objects.html'
    queryset = WorkObject.objects.all()
    context_object_name = 'work_objects'



#**********************************************************************************************************************#
#*************************************************** WORK OBJECT VIEW *************************************************#
#**********************************************************************************************************************#


def workObjectView(request, **kwargs):
    allusers = CustomUser.objects.all()
    work_object, created = WorkObject.objects.get_or_create(id=kwargs['pk'])
    users = work_object.user.all()
    messages = Message.objects.filter(
        work_object=work_object,
       )
    ############################################################
    ## get_or_create function wit the ManyToMany relationship ##
    #
    total, created = TotalWorkObject.objects.get_or_create(name=work_object.name)
    total.work_object.add(work_object)
    ############################################################
    u_total_coffee_food = 0
    obj_coffee_food = 0
    obj_fuel = 0
    obj_prepayment = 0
    obj_phone_costs = 0
    obj_sum_time_sec = 0
    obj_sum_over_time_sec = 0
    obj_work_time = 0
    finally_obj_work_time = 0
    # obj_work_over_time = 0
    for user in users:
        ############################################
        ### Totals of all costs i current object ###
        total_coffee_food = Work.objects.filter(
            user__id=user.id, 
            work_object=work_object
            ).aggregate(
            total_coffee_food=Sum('coffee_food')
            )['total_coffee_food']
        if total_coffee_food is not None:
            obj_coffee_food += total_coffee_food
            # total.obj_coffee_food = F('obj_coffee_food') + total_coffee_food

        total_fuel = Work.objects.filter(
            user__id=user.id, 
            work_object=work_object
            ).aggregate(
            total_fuel=Sum('fuel')
            )['total_fuel']
        if total_fuel is not None:
            obj_fuel += total_fuel

        total_prepayment = Work.objects.filter(
            user__id=user.id, 
            work_object=work_object
            ).aggregate(
            total_prepayment=Sum('prepayment')
            )['total_prepayment']
        if total_prepayment is not None:
            obj_prepayment += total_prepayment

        total_phone_costs = Work.objects.filter(
            user__id=user.id, 
            work_object=work_object
            ).aggregate(
            total_phone_costs=Sum('phone_costs')
            )['total_phone_costs']
        if total_phone_costs is not None:
            obj_phone_costs += total_phone_costs

        total_sum_time_sec = Work.objects.filter(
            user__id=user.id, 
            work_object=work_object
            ).aggregate(
            total_sum_time_sec=Sum('sum_time_sec')
            )['total_sum_time_sec']
        if total_sum_time_sec is not None:
            obj_sum_time_sec += total_sum_time_sec

        total_sum_over_time_sec = Work.objects.filter(
            user__id=user.id, 
            work_object=work_object
            ).aggregate(
            total_sum_over_time_sec=Sum('sum_over_time_sec')
            )['total_sum_over_time_sec']
        if total_sum_over_time_sec is not None:
            obj_sum_over_time_sec += total_sum_over_time_sec

        if total_sum_time_sec:
            ### total_sum_time_sec => hours:minutes ###
            total_hours = obj_sum_time_sec // 3600
            total_sec = obj_sum_time_sec % 3600
            total_min = total_sec // 60
            obj_work_time = f'{int(total_hours)}:{int(total_min)}'
            if obj_work_time is not None:
                finally_obj_work_time = obj_work_time
        else:
            obj_work_time = '0:00'
        if total_sum_over_time_sec:
            ### total_sum_over_time_sec => hours:minutes ###
            total_hours = obj_sum_over_time_sec // 3600
            total_sec = obj_sum_over_time_sec % 3600
            total_min = total_sec // 60
            if total_min < 10 or total_min == 0.0:
                obj_sum_over_time = f'{int(total_hours)}:0{int(total_min)}'
            else:
                obj_sum_over_time = f'{int(total_hours)}:{int(total_min)}'
        else:
            obj_sum_over_time = '0:00'
            
        ### End Totals for all ###
        ##########################
    
    ## Add new user to the object & make chat with all users belong to it
    if request.method == 'POST':
        ## Add new user in work object
        if 'add_user' in request.POST:
            user = request.POST.get('user')
            add_user = CustomUser.objects.get(username=user)
            work_object.user.add(add_user)
            work_object.save()
            work_object, created = WorkObject.objects.get_or_create(id=kwargs['pk'])
            users = work_object.user.all()
            print('++')
        ## Add new message to the chat
        # elif 'chat' in request.POST:
        #     r_user = request.user
        #     content = request.POST.get('content')
        #     messages = Message.objects.filter(
        #         work_object=work_object,
        #     )
        #     new_message = Message(
        #         name = r_user,
        #         sender=r_user,
        #         content=content,
        #         work_object=work_object
        #     )
        #     new_message.save()
        #     response = {
        #         'new_message_id': new_message.id
        #     }
        #     print('--')

    context = {
        'current_time': datetime.now().strftime('%Y-%m-%d'),
        'messages': messages,
        'work_object': work_object,
        'users': users,
        'allusers': allusers,
        'finally_obj_work_time': finally_obj_work_time,
        'obj_coffee_food': obj_coffee_food,
        "obj_fuel": obj_fuel,
        'obj_prepayment': obj_prepayment,
        'obj_phone_costs': obj_phone_costs,
        'obj_sum_time_sec': obj_sum_time_sec,
        'obj_sum_over_time_sec': obj_sum_over_time_sec,
        'obj_work_time': obj_work_time,
        'u_total_coffee_food': u_total_coffee_food,
    }
    return render(request, 'work_object.html', context)


def chat(request, pk):
    if request.method == 'GET':
        path = pk
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        work_object, created = WorkObject.objects.get_or_create(id=pk)
        messages = Message.objects.filter(
                    work_object=work_object,
                )
        response = {
            'user': request.user.username,
            'messages': list(messages.values()),
            'current_time': current_time,
        }
        return JsonResponse(response)
    if request.method == 'POST':
        work_object, created = WorkObject.objects.get_or_create(id=pk)
        r_user = request.user
        content = request.POST.get('txt')
        messages = Message.objects.filter(
            work_object=work_object,
        )
        new_message = Message(
            name = r_user,
            sender=r_user,
            content=content,
            day = f"{datetime.now().strftime('%d %B %Y')}  ",
            time = f'{datetime.now().hour}:{datetime.now().minute}',
            work_object=work_object,
        )
        new_message.save()
        response = {
            'new_message_id': new_message.id
        }
        print('--')
        return JsonResponse(response)



#**********************************************************************************************************************#
#************************************************** CREATE WORK OBJECT ************************************************#
#**********************************************************************************************************************#


def createWorkObject(request):
    users = CustomUser.objects.all()
    if request.method == 'POST':
        users = CustomUser.objects.all()
        work = WorkObject.objects.create()
        workname = request.POST.get('workname')
        print('workname ---', workname)
        if workname != '':
            work.name = workname
            print('workname +++', workname)
            users_email = request.POST.getlist('users')
            print('user_email: ', users_email)
            print('users: ', users)
            work.user.add(*users_email)
            work.save()
            return redirect('work_objects')
        work_none = WorkObject.objects.filter(name=None)
        work_none.delete()
        return redirect('home')
    context = {
        'users': users,
    }
    return render(request, 'create_work_object.html', context)


#**********************************************************************************************************************#
#*************************************************** CREATE WORK-TYPE *************************************************#
#**********************************************************************************************************************#


def createWorkType(request):
    users = CustomUser.objects.all()
    if request.method == 'POST':
        users = CustomUser.objects.all()
        worktype = WorkType.objects.create()
        worktype_name = request.POST.get('worktype_name')
        if worktype_name != '':
            worktype.name = worktype_name
            users_email = request.POST.getlist('users')
            worktype.user.add(*users_email)
            worktype.save()
            return redirect('work_objects')
        work_none = WorkType.objects.filter(name=None)
        work_none.delete()
        return redirect('home')
    context = {
        'users': users,
    }
    return render(request, 'create_work_type.html', context)


#**********************************************************************************************************************#
#************************************************* USER CREATE HIS WORK ***********************************************#
#**********************************************************************************************************************#


def userWork(request, pk):
    if request.method == 'POST':
        date = request.POST.get('date')
        timestart = request.POST.get('timestart')
        timefinish = request.POST.get('timefinish')

        ### Here we need to make str(date) => int(date) to sum it ###
        year, month, day = date.split('-')
        start_hr, start_min = timestart.split(':') 
        finish_hr, finish_min = timefinish.split(':') 
        start = datetime(int(year), int(month), int(day), int(start_hr), int(start_min))
        end = datetime(int(year), int(month), int(day), int(finish_hr), int(finish_min))
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

        work_object = request.POST.get('work_object')
        work_type = request.POST.get('work_type')
        coffee_food = request.POST.get('coffee_food')
        fuel = request.POST.get('fuel')
        prepayment = request.POST.get('prepayment')
        phone_costs = request.POST.get('phone_costs')
        user = CustomUser.objects.get(id=pk)
        work = Work.objects.create()
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
        work.coffee_food = coffee_food
        work.prepayment = prepayment
        work.fuel = fuel
        work.phone_costs = phone_costs
        work.payment = (user.payment / 3600) * diff.seconds
        work.user.add(user)
        work.save()
        return redirect('user_work', pk=pk)
    else:
        allworks = Work.objects.filter(user__id=pk)
        work_objects = WorkObject.objects.filter(user__id=pk)
        work_type = WorkType.objects.all()
        total_coffee_food = Work.objects.filter(user__id=pk).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
        if total_coffee_food is not None:
            total_coffee_food = '{:.2f}'.format(total_coffee_food)
        total_fuel = Work.objects.filter(user__id=pk).aggregate(total_fuel=Sum('fuel'))['total_fuel']
        if total_fuel is not None:
            total_fuel = '{:.2f}'.format(total_fuel)
        total_prepayment = Work.objects.filter(user__id=pk).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
        if total_prepayment is not None:
            total_prepayment = '{:.2f}'.format(total_prepayment)
        total_phone_costs = Work.objects.filter(user__id=pk).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
        if total_phone_costs is not None:
            total_phone_costs = '{:.2f}'.format(total_phone_costs)
        total_payment = Work.objects.filter(user__id=pk).aggregate(total_payment=Sum('payment'))['total_payment']
        if total_payment is not None:
            total_payment = '{:.2f}'.format(total_payment)
        total_sum_time_sec = Work.objects.filter(user__id=pk).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
        total_sum_over_time_sec = Work.objects.filter(user__id=pk).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

        if total_sum_time_sec:
            ### total_sum_time_sec => hours:minutes ###
            total_hours = total_sum_time_sec // 3600
            total_sec = total_sum_time_sec % 3600
            total_min = total_sec // 60
            if total_min < 10 or total_min == 0.0:
                total_work_time = f'{int(total_hours)}:0{int(total_min)}'
            else:
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
        else:
            total_work_time = '0:00'

        if total_sum_over_time_sec:
            ### total_sum_over_time_sec => hours:minutes ###
            total_hours = total_sum_over_time_sec // 3600
            total_sec = total_sum_over_time_sec % 3600
            total_min = total_sec // 60
            if total_min < 10 or total_min == 0.0:
                total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
            else:
                total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
        else:
            total_work_over_time = '0:00'

    context = {
        'allworks': allworks,
        'work_objects': work_objects,
        'work_type': work_type,
        'total_coffee_food': total_coffee_food,
        'total_fuel': total_fuel,
        'total_prepayment' : total_prepayment,
        'total_phone_costs': total_phone_costs,
        'total_payment': total_payment,
        'total_work_time': total_work_time,
        'total_work_over_time': total_work_over_time,
        }
    return render(request, 'user_work.html', context)


#**********************************************************************************************************************#
#************************************************** UPDATE USER WORK **************************************************#
#**********************************************************************************************************************#

def updateUserWork(request, work_pk):
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

        ### Here we need to make str(date) => int(date) to sum it ###
        year, month, day = date.split('-')
        start_hr, start_min = timestart.split(':') 
        finish_hr, finish_min = timefinish.split(':') 
        start = datetime(int(year), int(month), int(day), int(start_hr), int(start_min))
        end = datetime(int(year), int(month), int(day), int(finish_hr), int(finish_min))
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

        work_object = request.POST.get('work_object')
        work_type = request.POST.get('work_type')
        coffee_food = request.POST.get('coffee_food')
        fuel = request.POST.get('fuel')
        prepayment = request.POST.get('prepayment')
        phone_costs = request.POST.get('phone_costs')
        # work = Work.objects.get(id=work_pk)
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
        work.coffee_food = coffee_food
        work.prepayment = prepayment
        work.fuel = fuel
        work.phone_costs = phone_costs
        work.payment = (user.payment / 3600) * diff.seconds       
        work.save()
        # return redirect('user_work', user.id)
        return redirect('raports')
    else:
        # work_o = Work.objects.get(id=work_pk)
        work_objects = WorkObject.objects.filter(user__id=user.id)
        work_type = WorkType.objects.all()

    context = {
        'work': work,
        'work_objects': work_objects,
        'work_type': work_type,
        }
    return render(request, 'update_user_work.html', context)


#**********************************************************************************************************************#
#****************************************************** USER RAPORT ***************************************************#
#**********************************************************************************************************************#


def getUserRaport(request, user_pk):
    work_objects = WorkObject.objects.filter(user__id=user_pk)
    works = Work.objects.filter(user__id=user_pk).order_by('date')
    ######################
    ### Totals for all ###
    total_coffee_food = Work.objects.filter(user__id=user_pk,).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
    total_fuel = Work.objects.filter(user__id=user_pk).aggregate(total_fuel=Sum('fuel'))['total_fuel']
    total_prepayment = Work.objects.filter(user__id=user_pk).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
    total_phone_costs = Work.objects.filter(user__id=user_pk).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
    total_payment = Work.objects.filter(user__id=user_pk).aggregate(total_payment=Sum('payment'))['total_payment']
    total_sum_time_sec = Work.objects.filter(user__id=user_pk).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
    total_sum_over_time_sec = Work.objects.filter(user__id=user_pk).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

    if total_sum_time_sec: 
        ### total_sum_time_sec => hours:minutes ###
        total_hours = total_sum_time_sec // 3600
        total_sec = total_sum_time_sec % 3600
        total_min = total_sec // 60
        total_work_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_time = '0:00'
    if total_sum_over_time_sec:
        ### total_sum_over_time_sec => hours:minutes ###
        total_hours = total_sum_over_time_sec // 3600
        total_sec = total_sum_over_time_sec % 3600
        total_min = total_sec // 60
        if total_min < 10 or total_min == 0.0:
            total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
        else:
            total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_over_time = '0:00'

    ### End Totals for all ###
    ##########################

    if request.method == 'POST':
        ### Sorted by date ###
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
            works = Work.objects.filter(
                date__range=(start, end),
                user__id=user_pk,
            ).order_by('date')
            ##############################
            ### Totals for sorted_from ###
            total_coffee_food = Work.objects.filter(date__range=(start, end)).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
            total_fuel = Work.objects.filter(date__range=(start, end)).aggregate(total_fuel=Sum('fuel'))['total_fuel']
            total_prepayment = Work.objects.filter(date__range=(start, end)).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
            total_phone_costs = Work.objects.filter(date__range=(start, end)).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
            total_payment = Work.objects.filter(date__range=(start, end)).aggregate(total_payment=Sum('payment'))['total_payment']
            total_sum_time_sec = Work.objects.filter(date__range=(start, end)).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
            total_sum_over_time_sec = Work.objects.filter(date__range=(start, end)).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

            if total_sum_time_sec:
                ### total_sum_time_sec => hours:minutes ###
                total_hours = total_sum_time_sec // 3600
                total_sec = total_sum_time_sec % 3600
                total_min = total_sec // 60
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_time = '0:00'
            if total_sum_over_time_sec:
                ### total_sum_over_time_sec => hours:minutes ###
                total_hours = total_sum_over_time_sec // 3600
                total_sec = total_sum_over_time_sec % 3600
                total_min = total_sec // 60
                if total_min < 10 or total_min == 0.0:
                    total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
                else:
                    total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_over_time = '0:00'
            ### End Totals for sorted_from ###
            ##################################

        
        #####################################################################################
        ###################################  WORK OBJECT  ###################################
        #####################################################################################
        if work_object: 
            works = Work.objects.filter(
                work_object=work_object,
                user__id=user_pk,
                ).order_by('date')
            ##############################
            ### Totals for sorted_from ###
            total_coffee_food = Work.objects.filter(work_object=work_object,).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
            total_fuel = Work.objects.filter(work_object=work_object,).aggregate(total_fuel=Sum('fuel'))['total_fuel']
            total_prepayment = Work.objects.filter(work_object=work_object,).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
            total_phone_costs = Work.objects.filter(work_object=work_object,).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
            total_payment = Work.objects.filter(work_object=work_object,).aggregate(total_payment=Sum('payment'))['total_payment']
            total_sum_time_sec = Work.objects.filter(work_object=work_object,).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
            total_sum_over_time_sec = Work.objects.filter(work_object=work_object,).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

            if total_sum_time_sec:
                ### total_sum_time_sec => hours:minutes ###
                total_hours = total_sum_time_sec // 3600
                total_sec = total_sum_time_sec % 3600
                total_min = total_sec // 60
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_time = '0:00'
            if total_sum_over_time_sec:
                ### total_sum_over_time_sec => hours:minutes ###
                total_hours = total_sum_over_time_sec // 3600
                total_sec = total_sum_over_time_sec % 3600
                total_min = total_sec // 60
                if total_min < 10 or total_min == 0.0:
                    total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
                else:
                    total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_over_time = '0:00'
            ### End Totals for sorted_from ###
            ################################## 


        
        #####################################################################################
        ##########################  SORTED FROM & WORK OBJECT  ##############################
        #####################################################################################
        if sorted_from and work_object:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))
            works = Work.objects.filter(
                date__range=(start, end),
                work_object=work_object,
                user__id=user_pk,
            ).order_by('date')
            ##############################
            ### Totals for sorted_from ###
            total_coffee_food = Work.objects.filter(date__range=(start, end), work_object=work_object,).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
            total_fuel = Work.objects.filter(date__range=(start, end), work_object=work_object,).aggregate(total_fuel=Sum('fuel'))['total_fuel']
            total_prepayment = Work.objects.filter(date__range=(start, end),work_object=work_object,).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
            total_phone_costs = Work.objects.filter(date__range=(start, end), work_object=work_object,).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
            total_payment = Work.objects.filter(date__range=(start, end), work_object=work_object,).aggregate(total_payment=Sum('payment'))['total_payment']
            total_sum_time_sec = Work.objects.filter(date__range=(start, end), work_object=work_object,).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
            total_sum_over_time_sec = Work.objects.filter(date__range=(start, end), work_object=work_object,).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

            if total_sum_time_sec:
                ### total_sum_time_sec => hours:minutes ###
                total_hours = total_sum_time_sec // 3600
                total_sec = total_sum_time_sec % 3600
                total_min = total_sec // 60
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_time = '0:00'
            if total_sum_over_time_sec:
                ### total_sum_over_time_sec => hours:minutes ###
                total_hours = total_sum_over_time_sec // 3600
                total_sec = total_sum_over_time_sec % 3600
                total_min = total_sec // 60
                if total_min < 10 or total_min == 0.0:
                    total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
                else:
                    total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_over_time = '0:00'
            ### End Totals for sorted_from ###
            ##################################


    context = {
        'works': works,
        'work_objects': work_objects,
        'total_coffee_food': total_coffee_food,
        'total_fuel': total_fuel,
        'total_prepayment': total_prepayment,
        'total_phone_costs': total_phone_costs,
        'total_payment': total_payment,
        'total_work_time': total_work_time,
        'total_work_over_time': total_work_over_time,
    }
    return render(request, 'user_raport.html', context)


#**********************************************************************************************************************#
#*************************************************** WORK OBJECT RAPORT ***********************************************#
#**********************************************************************************************************************#


def workObjectRaport(request, user_pk, object_pk):
    #########################
    ### Totals for choice ###

    total_coffee_food = Work.objects.filter(user__id=user_pk).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
    total_fuel = Work.objects.filter(user__id=user_pk).aggregate(total_fuel=Sum('fuel'))['total_fuel']
    total_prepayment = Work.objects.filter(user__id=user_pk).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
    total_phone_costs = Work.objects.filter(user__id=user_pk).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
    total_payment = Work.objects.filter(user__id=user_pk).aggregate(total_payment=Sum('payment'))['total_payment']
    total_sum_time_sec = Work.objects.filter(user__id=user_pk).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
    total_sum_over_time_sec = Work.objects.filter(user__id=user_pk).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

    if total_sum_time_sec:
        ### total_sum_time_sec => hours:minutes ###
        total_hours = total_sum_time_sec // 3600
        total_sec = total_sum_time_sec % 3600
        total_min = total_sec // 60
        total_work_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_time = '0:00'
    if total_sum_over_time_sec:
        ### total_sum_over_time_sec => hours:minutes ###
        total_hours = total_sum_over_time_sec // 3600
        total_sec = total_sum_over_time_sec % 3600
        total_min = total_sec // 60
        if total_min < 10 or total_min == 0.0:
            total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
        else:
            total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_over_time = '0:00'

    ### End Totals for choice ###
    #############################

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
            work_object = WorkObject.objects.get(
                pk=object_pk,
                # user__id=user_pk,
                )

             ### Sorted by date continue.. ###
            work_by_date = Work.objects.filter(
                user__id=user_pk,
                date__range=(start, end),
                work_object=work_object.name,
            ).order_by('date')

            #########################
            ### Totals for choice ###
            total_coffee_food = Work.objects.filter(date__range=(start, end), user__id=user_pk, work_object=work_object.name,).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
            total_fuel = Work.objects.filter(date__range=(start, end), user__id=user_pk, work_object=work_object.name,).aggregate(total_fuel=Sum('fuel'))['total_fuel']
            total_prepayment = Work.objects.filter(date__range=(start, end), user__id=user_pk, work_object=work_object.name,).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
            total_phone_costs = Work.objects.filter(date__range=(start, end), user__id=user_pk, work_object=work_object.name,).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
            total_payment = Work.objects.filter(date__range=(start, end), user__id=user_pk, work_object=work_object.name,).aggregate(total_payment=Sum('payment'))['total_payment']
            total_sum_time_sec = Work.objects.filter(date__range=(start, end), user__id=user_pk, work_object=work_object.name,).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
            total_sum_over_time_sec = Work.objects.filter(date__range=(start, end), user__id=user_pk, work_object=work_object.name,).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

            if total_sum_time_sec:
                ### total_sum_time_sec => hours:minutes ###
                total_hours = total_sum_time_sec // 3600
                total_sec = total_sum_time_sec % 3600
                total_min = total_sec // 60
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_time = '0:00'
            if total_sum_over_time_sec:
                ### total_sum_over_time_sec => hours:minutes ###
                total_hours = total_sum_over_time_sec // 3600
                total_sec = total_sum_over_time_sec % 3600
                total_min = total_sec // 60
                if total_min < 10 or total_min == 0.0:
                    total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
                else:
                    total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_over_time = '0:00'

            ### End Totals for choice ###
            #############################

    else:
        ### Sorted by workobject ###
        work_object = WorkObject.objects.get(
            pk=object_pk,
            # user__id=user_pk,
            )
        # wo = WorkObject.objects.get(id=work_object)
        ### Sorted by date continue.. ###
        work_by_date = Work.objects.filter(
            user__id=user_pk,
            work_object=work_object.name,
        ).order_by('date')

        #########################
        ### Totals for choice ###
        total_coffee_food = Work.objects.filter(user__id=user_pk, work_object=work_object.name,).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
        total_fuel = Work.objects.filter(user__id=user_pk, work_object=work_object.name,).aggregate(total_fuel=Sum('fuel'))['total_fuel']
        total_prepayment = Work.objects.filter(user__id=user_pk, work_object=work_object.name,).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
        total_phone_costs = Work.objects.filter(user__id=user_pk, work_object=work_object.name,).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
        total_payment = Work.objects.filter(user__id=user_pk, work_object=work_object.name,).aggregate(total_payment=Sum('payment'))['total_payment']
        total_sum_time_sec = Work.objects.filter(user__id=user_pk, work_object=work_object.name,).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
        total_sum_over_time_sec = Work.objects.filter(user__id=user_pk, work_object=work_object.name,).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

        if total_sum_time_sec:
            ### total_sum_time_sec => hours:minutes ###
            total_hours = total_sum_time_sec // 3600
            total_sec = total_sum_time_sec % 3600
            total_min = total_sec // 60
            total_work_time = f'{int(total_hours)}:{int(total_min)}'
        else:
            total_work_time = '0:00'
        if total_sum_over_time_sec:
            ### total_sum_over_time_sec => hours:minutes ###
            total_hours = total_sum_over_time_sec // 3600
            total_sec = total_sum_over_time_sec % 3600
            total_min = total_sec // 60
            if total_min < 10 or total_min == 0.0:
                total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
            else:
                total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
        else:
            total_work_over_time = '0:00'

        ### End Totals for choice ###
        #############################

    context = {
        'work_by_date': work_by_date,
        'work_object': work_object,
        'total_coffee_food': total_coffee_food,
        'total_fuel': total_fuel,
        'total_prepayment': total_prepayment,
        'total_phone_costs': total_phone_costs,
        'total_payment': total_payment,
        'total_work_time': total_work_time,
        'total_work_over_time': total_work_over_time,
    }
    return render(request, 'workobject_raport.html', context)


#**********************************************************************************************************************#
#****************************************************** ALL RAPORTS ***************************************************#
#**********************************************************************************************************************#


def raports(request):
    works = Work.objects.prefetch_related('user').order_by('date')
    users = CustomUser.objects.all()
    work_objects = WorkObject.objects.all()

    ##############################
    ### Totals for sorted_from ###
    total_coffee_food = Work.objects.all().aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
    total_fuel = Work.objects.all().aggregate(total_fuel=Sum('fuel'))['total_fuel']
    total_prepayment = Work.objects.all().aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
    total_phone_costs = Work.objects.all().aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
    total_payment = Work.objects.all().aggregate(total_payment=Sum('payment'))['total_payment']
    total_sum_time_sec = Work.objects.all().aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
    total_sum_over_time_sec = Work.objects.all().aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

    if total_sum_time_sec:
        ### total_sum_time_sec => hours:minutes ###
        total_hours = total_sum_time_sec // 3600
        total_sec = total_sum_time_sec % 3600
        total_min = total_sec // 60
        total_work_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_time = '0:00'
    if total_sum_over_time_sec:
        ### total_sum_over_time_sec => hours:minutes ###
        total_hours = total_sum_over_time_sec // 3600
        total_sec = total_sum_over_time_sec % 3600
        total_min = total_sec // 60
        if total_min < 10 or total_min == 0.0:
            total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
        else:
            total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_over_time = '0:00'
    ### End Totals for sorted_from ###
    ##################################

    if request.method == 'POST':
        sorted_from = request.POST.get('sorted_from')
        user = request.POST.get('user')
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
            works = Work.objects.prefetch_related('user').filter(
                date__range=(start, end),
            ).order_by('date')
            ##############################
            ### Totals for sorted_from ###
            total_coffee_food = Work.objects.filter(date__range=(start, end)).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
            total_fuel = Work.objects.filter(date__range=(start, end)).aggregate(total_fuel=Sum('fuel'))['total_fuel']
            total_prepayment = Work.objects.filter(date__range=(start, end)).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
            total_phone_costs = Work.objects.filter(date__range=(start, end)).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
            total_payment = Work.objects.filter(date__range=(start, end)).aggregate(total_payment=Sum('payment'))['total_payment']
            total_sum_time_sec = Work.objects.filter(date__range=(start, end)).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
            total_sum_over_time_sec = Work.objects.filter(date__range=(start, end)).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

            if total_sum_time_sec:
                ### total_sum_time_sec => hours:minutes ###
                total_hours = total_sum_time_sec // 3600
                total_sec = total_sum_time_sec % 3600
                total_min = total_sec // 60
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_time = '0:00'
            if total_sum_over_time_sec:
                ### total_sum_over_time_sec => hours:minutes ###
                total_hours = total_sum_over_time_sec // 3600
                total_sec = total_sum_over_time_sec % 3600
                total_min = total_sec // 60
                if total_min < 10 or total_min == 0.0:
                    total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
                else:
                    total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_over_time = '0:00'
            ### End Totals for sorted_from ###
            ##################################


        #####################################################################################
        #######################################  USER  ######################################
        #####################################################################################
        if user:
            user = CustomUser.objects.get(username=user)
            works = Work.objects.filter(user=user).order_by('date')
            ##############################
            ### Totals for sorted_from ###
            total_coffee_food = Work.objects.filter(user__id=user.id).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
            total_fuel = Work.objects.filter(user__id=user.id).aggregate(total_fuel=Sum('fuel'))['total_fuel']
            total_prepayment = Work.objects.filter(user__id=user.id).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
            total_phone_costs = Work.objects.filter(user__id=user.id).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
            total_payment = Work.objects.filter(user__id=user.id).aggregate(total_payment=Sum('payment'))['total_payment']
            total_sum_time_sec = Work.objects.filter(user__id=user.id).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
            total_sum_over_time_sec = Work.objects.filter(user__id=user.id).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

            if total_sum_time_sec:
                ### total_sum_time_sec => hours:minutes ###
                total_hours = total_sum_time_sec // 3600
                total_sec = total_sum_time_sec % 3600
                total_min = total_sec // 60
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_time = '0:00'
            if total_sum_over_time_sec:
                ### total_sum_over_time_sec => hours:minutes ###
                total_hours = total_sum_over_time_sec // 3600
                total_sec = total_sum_over_time_sec % 3600
                total_min = total_sec // 60
                if total_min < 10 or total_min == 0.0:
                    total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
                else:
                    total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_over_time = '0:00'
            ### End Totals for sorted_from ###
            ##################################


        #####################################################################################
        ###################################  WORK OBJECT  ###################################
        #####################################################################################
        if work_object: 
            wo = WorkObject.objects.get(id=work_object)
            works = Work.objects.filter(work_object=wo.name).order_by('date')
            print('WORK_OBJECT:', wo.name)
            ##############################
            ### Totals for sorted_from ###
            total_coffee_food = Work.objects.filter(work_object=wo.name,).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
            total_fuel = Work.objects.filter(work_object=wo.name,).aggregate(total_fuel=Sum('fuel'))['total_fuel']
            total_prepayment = Work.objects.filter(work_object=wo.name,).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
            total_phone_costs = Work.objects.filter(work_object=wo.name,).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
            total_payment = Work.objects.filter(work_object=wo.name,).aggregate(total_payment=Sum('payment'))['total_payment']
            total_sum_time_sec = Work.objects.filter(work_object=wo.name,).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
            total_sum_over_time_sec = Work.objects.filter(work_object=wo.name,).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

            if total_sum_time_sec:
                ### total_sum_time_sec => hours:minutes ###
                total_hours = total_sum_time_sec // 3600
                total_sec = total_sum_time_sec % 3600
                total_min = total_sec // 60
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_time = '0:00'
            if total_sum_over_time_sec:
                ### total_sum_over_time_sec => hours:minutes ###
                total_hours = total_sum_over_time_sec // 3600
                total_sec = total_sum_over_time_sec % 3600
                total_min = total_sec // 60
                if total_min < 10 or total_min == 0.0:
                    total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
                else:
                    total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_over_time = '0:00'
            ### End Totals for sorted_from ###
            ################################## 


        #####################################################################################
        ##########################  SORTED FROM & WORK OBJECT  ##############################
        #####################################################################################
        if sorted_from and work_object:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))
            works = Work.objects.prefetch_related('user').filter(
                date__range=(start, end),
                work_object=work_object,
            ).order_by('date')
            wo = WorkObject.objects.get(id=work_object)
            ##############################
            ### Totals for sorted_from ###
            total_coffee_food = Work.objects.filter(date__range=(start, end), work_object=wo.name,).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
            total_fuel = Work.objects.filter(date__range=(start, end), work_object=wo.name,).aggregate(total_fuel=Sum('fuel'))['total_fuel']
            total_prepayment = Work.objects.filter(date__range=(start, end),work_object=wo.name,).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
            total_phone_costs = Work.objects.filter(date__range=(start, end), work_object=wo.name,).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
            total_payment = Work.objects.filter(date__range=(start, end), work_object=wo.name,).aggregate(total_payment=Sum('payment'))['total_payment']
            total_sum_time_sec = Work.objects.filter(date__range=(start, end), work_object=wo.name,).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
            total_sum_over_time_sec = Work.objects.filter(date__range=(start, end), work_object=wo.name,).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

            if total_sum_time_sec:
                ### total_sum_time_sec => hours:minutes ###
                total_hours = total_sum_time_sec // 3600
                total_sec = total_sum_time_sec % 3600
                total_min = total_sec // 60
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_time = '0:00'
            if total_sum_over_time_sec:
                ### total_sum_over_time_sec => hours:minutes ###
                total_hours = total_sum_over_time_sec // 3600
                total_sec = total_sum_over_time_sec % 3600
                total_min = total_sec // 60
                if total_min < 10 or total_min == 0.0:
                    total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
                else:
                    total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_over_time = '0:00'
            ### End Totals for sorted_from ###
            ##################################


        #####################################################################################
        #################################  SORTED FROM & USER  ##############################
        #####################################################################################
        if sorted_from and user:
            user = CustomUser.objects.get(username=user)
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))
            works = Work.objects.prefetch_related('user').filter(
                date__range=(start, end),
                user=user,
            ).order_by('date')

            ##############################
            ### Totals for sorted_from ###
            total_coffee_food = Work.objects.filter(date__range=(start, end), user__id=user.id).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
            total_fuel = Work.objects.filter(date__range=(start, end), user__id=user.id).aggregate(total_fuel=Sum('fuel'))['total_fuel']
            total_prepayment = Work.objects.filter(date__range=(start, end), user__id=user.id).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
            total_phone_costs = Work.objects.filter(date__range=(start, end), user__id=user.id).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
            total_payment = Work.objects.filter(date__range=(start, end), user__id=user.id).aggregate(total_payment=Sum('payment'))['total_payment']
            total_sum_time_sec = Work.objects.filter(date__range=(start, end), user__id=user.id).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
            total_sum_over_time_sec = Work.objects.filter(date__range=(start, end), user__id=user.id).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

            if total_sum_time_sec:
                ### total_sum_time_sec => hours:minutes ###
                total_hours = total_sum_time_sec // 3600
                total_sec = total_sum_time_sec % 3600
                total_min = total_sec // 60
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_time = '0:00'
            if total_sum_over_time_sec:
                ### total_sum_over_time_sec => hours:minutes ###
                total_hours = total_sum_over_time_sec // 3600
                total_sec = total_sum_over_time_sec % 3600
                total_min = total_sec // 60
                if total_min < 10 or total_min == 0.0:
                    total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
                else:
                    total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_over_time = '0:00'
            ### End Totals for sorted_from ###
            ##################################


        #####################################################################################
        #################################  WORK OBJECT & USER  ##############################
        #####################################################################################
        if work_object and user:
            # user = CustomUser.objects.get(username=user)
            works = Work.objects.filter(
                work_object=work_object,
                user=user
                ).order_by('date')
            wo = WorkObject.objects.get(id=work_object)
            ##############################
            ### Totals for sorted_from ###
            total_coffee_food = Work.objects.filter(user__id=user.id, work_object=wo.name,).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
            total_fuel = Work.objects.filter(user__id=user.id, work_object=wo.name,).aggregate(total_fuel=Sum('fuel'))['total_fuel']
            total_prepayment = Work.objects.filter(user__id=user.id, work_object=wo.name,).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
            total_phone_costs = Work.objects.filter(user__id=user.id, work_object=wo.name,).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
            total_payment = Work.objects.filter(user__id=user.id, work_object=wo.name,).aggregate(total_payment=Sum('payment'))['total_payment']
            total_sum_time_sec = Work.objects.filter(user__id=user.id, work_object=wo.name,).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
            total_sum_over_time_sec = Work.objects.filter(user__id=user.id, work_object=wo.name,).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

            if total_sum_time_sec:
                ### total_sum_time_sec => hours:minutes ###
                total_hours = total_sum_time_sec // 3600
                total_sec = total_sum_time_sec % 3600
                total_min = total_sec // 60
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_time = '0:00'
            if total_sum_over_time_sec:
                ### total_sum_over_time_sec => hours:minutes ###
                total_hours = total_sum_over_time_sec // 3600
                total_sec = total_sum_over_time_sec % 3600
                total_min = total_sec // 60
                if total_min < 10 or total_min == 0.0:
                    total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
                else:
                    total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_over_time = '0:00'
            ## End Totals for sorted_from ###
            #################################


        #####################################################################################
        ##########################  SORTED FROM & WORK OBJECT & USER  #######################
        #####################################################################################  
        if sorted_from and user and work_object:
            # user = CustomUser.objects.get(username=user)
            works = Work.objects.filter(
                date__range=(start, end),
                work_object=work_object,
                user=user,
            ).order_by('date')
            wo = WorkObject.objects.get(id=work_object)
            ##############################
            ### Totals for sorted_from ###
            total_coffee_food = Work.objects.filter(date__range=(start, end), user__id=user.id, work_object=wo.name,).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
            total_fuel = Work.objects.filter(date__range=(start, end), user__id=user.id, work_object=wo.name,).aggregate(total_fuel=Sum('fuel'))['total_fuel']
            total_prepayment = Work.objects.filter(date__range=(start, end), user__id=user.id, work_object=wo.name,).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
            total_phone_costs = Work.objects.filter(date__range=(start, end), user__id=user.id, work_object=wo.name,).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
            total_payment = Work.objects.filter(date__range=(start, end), user__id=user.id, work_object=wo.name,).aggregate(total_payment=Sum('payment'))['total_payment']
            total_sum_time_sec = Work.objects.filter(date__range=(start, end), user__id=user.id, work_object=wo.name,).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']
            total_sum_over_time_sec = Work.objects.filter(date__range=(start, end), user__id=user.id, work_object=wo.name,).aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec']

            if total_sum_time_sec:
                ### total_sum_time_sec => hours:minutes ###
                total_hours = total_sum_time_sec // 3600
                total_sec = total_sum_time_sec % 3600
                total_min = total_sec // 60
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_time = '0:00'
            if total_sum_over_time_sec:
                ### total_sum_over_time_sec => hours:minutes ###
                total_hours = total_sum_over_time_sec // 3600
                total_sec = total_sum_over_time_sec % 3600
                total_min = total_sec // 60
                if total_min < 10 or total_min == 0.0:
                    total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
                else:
                    total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_over_time = '0:00'
            ### End Totals for sorted_from ###
            ##################################

    
    context = {
        'works': works,
        'users': users, 
        'work_objects': work_objects,
        'total_coffee_food': total_coffee_food,
        'total_fuel': total_fuel,
        'total_prepayment': total_prepayment,
        'total_phone_costs': total_phone_costs,
        'total_payment': total_payment,
        'total_work_time': total_work_time,
        'total_work_over_time': total_work_over_time,
    }
    return render(request, 'raports.html', context)


#**********************************************************************************************************************#
#******************************************************* MESSAGES *****************************************************#
#**********************************************************************************************************************#


# @login_required
# def chat(request, receiver_id):
#     receiver = get_object_or_404(CustomUser, id=receiver_id)
#     messages = Message.objects.filter(
#         sender=request.user,
#         receiver=receiver
#     ) | Message.objects.filter(
#         sender=receiver,
#         receiver=request.user
#     ).order_by('timestamp')
#     return render(request, 'work_object.html', {'receiver': receiver, 'messages': messages})

# @login_required
# def send_message(request, receiver_id):
#     receiver = get_object_or_404(CustomUser, id=receiver_id)
#     if request.method == 'POST':
#         content = request.POST.get('content')
#         if content:
#             message = Message.objects.create(
#                 sender=request.user,
#                 receiver=receiver,
#                 content=content
#             )
#     return redirect('chat', receiver_id=receiver_id)