from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from .forms import WorkobjectForm
from .models import Work, WorkObject, WorkType
from django.http import HttpResponse
from django.db.models import Sum
from datetime import datetime

from users.models import CustomUser
def index(request):
    return render(request, "home.html")


class WorkObjects(ListView):
    model = WorkObject
    template_name = 'work_objects.html'
    queryset = WorkObject.objects.all()
    context_object_name = 'work_objects'


class WorkObjectView(DetailView):
    model = WorkObject
    template_name = 'work_object.html'

    def get_context_data(self, **kwargs):
        work_object = WorkObject.objects.get(id=self.kwargs['pk'])
        users = work_object.user.all()
        context = {
            'work_object': work_object,
            'users': users,
        }
        return context


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
        dif_hours = diff.seconds // 3600
        dif_sec = diff.seconds % 3600
        dif_min = dif_sec // 60
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
        work.sum_time_sec = diff.seconds
        work.work_object = work_object
        work.work_type = work_type
        work.coffee_food = coffee_food
        work.prepayment = prepayment
        work.fuel = fuel
        work.phone_costs = phone_costs
        work.user.add(user)
        work.save()
        print(diff)
        return redirect('user_work', pk=pk)
    else:
        allworks = Work.objects.filter(user__id=pk)
        work_objects = WorkObject.objects.filter(user__id=pk)
        work_type = WorkType.objects.all()
        total_coffee_food = Work.objects.filter(user__id=pk).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
        total_fuel = Work.objects.filter(user__id=pk).aggregate(total_fuel=Sum('fuel'))['total_fuel']
        total_prepayment = Work.objects.filter(user__id=pk).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
        total_phone_costs = Work.objects.filter(user__id=pk).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
        total_sum_time_sec = Work.objects.filter(user__id=pk).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']

        if total_sum_time_sec:
            ### total_sum_time_sec => hours:minutes ###
            total_hours = total_sum_time_sec // 3600
            total_sec = total_sum_time_sec % 3600
            total_min = total_sec // 60
            total_work_time = f'{int(total_hours)}:{int(total_min)}'
        else:
            total_work_time = '0:00'
    context = {
        'allworks': allworks,
        'work_objects': work_objects,
        'work_type': work_type,
        'total_coffee_food': total_coffee_food,
        'total_fuel': total_fuel,
        'total_prepayment' : total_prepayment,
        'total_phone_costs': total_phone_costs,
        'total_work_time': total_work_time,
        }
    return render(request, 'user_work.html', context)


def getRaport(request, user_pk):
    work_objects = WorkObject.objects.filter(user__id=user_pk)

    if request.method == 'POST':

        ### Sorted by date ###
        sorted_from = request.POST.get('sorted_from')
        year, month, day = sorted_from.split('-')
        sorted_to = request.POST.get('sorted_to')
        year_, month_, day_ = sorted_to.split('-')
        start = datetime(int(year), int(month), int(day))
        end = datetime(int(year_), int(month_), int(day_))
        ### Sorted by date pause.. ###

        ### Sorted by workobject ###
        work_object = request.POST.get('work_object')
        if work_object == '':
            work_by_date = Work.objects.filter(
            user__id=user_pk,
            date__range=(start, end),
            )
            user = CustomUser.objects.get(id=user_pk)
            work_objects = user.workobject_set.all()

            user = CustomUser.objects.get(id=user_pk)
            work_objects = user.workobject_set.all()

            ######################
            ### Totals for all ###
            total_coffee_food = Work.objects.filter(user__id=user_pk,).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
            total_fuel = Work.objects.filter(user__id=user_pk).aggregate(total_fuel=Sum('fuel'))['total_fuel']
            total_prepayment = Work.objects.filter(user__id=user_pk).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
            total_phone_costs = Work.objects.filter(user__id=user_pk).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
            total_sum_time_sec = Work.objects.filter(user__id=user_pk).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']

            if total_sum_time_sec:
                ### total_sum_time_sec => hours:minutes ###
                total_hours = total_sum_time_sec // 3600
                total_sec = total_sum_time_sec % 3600
                total_min = total_sec // 60
                total_work_time = f'{int(total_hours)}:{int(total_min)}'
            else:
                total_work_time = '0:00'
            ### End Totals for all ###
            ##########################

            context = {
                'work_by_date': work_by_date,
                'work_objects': work_objects,
                'total_coffee_food': total_coffee_food,
            }
            return render(request, 'user_raport.html', context)
        
        ### Sorted by date continue.. ###
        work_by_date = Work.objects.filter(
            user__id=user_pk,
            date__range=(start, end),
            work_object=work_object,
        )
        user = CustomUser.objects.get(id=user_pk)
        work_objects = user.workobject_set.all()

        #########################
        ### Totals for choice ###
        total_coffee_food = Work.objects.filter(user__id=user_pk, work_object=work_object,).aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food']
        total_fuel = Work.objects.filter(user__id=user_pk).aggregate(total_fuel=Sum('fuel'))['total_fuel']
        total_prepayment = Work.objects.filter(user__id=user_pk).aggregate(total_prepayment=Sum('prepayment'))['total_prepayment']
        total_phone_costs = Work.objects.filter(user__id=user_pk).aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs']
        total_sum_time_sec = Work.objects.filter(user__id=user_pk).aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec']

        if total_sum_time_sec:
            ### total_sum_time_sec => hours:minutes ###
            total_hours = total_sum_time_sec // 3600
            total_sec = total_sum_time_sec % 3600
            total_min = total_sec // 60
            total_work_time = f'{int(total_hours)}:{int(total_min)}'
        else:
            total_work_time = '0:00'
        ### End Totals for choice ###
        #############################

        context = {
            'work_by_date': work_by_date,
            'work_objects': work_objects,
            'total_coffee_food': total_coffee_food,
        }
        return render(request, 'user_raport.html', context)

    return render(request, 'user_raport.html')