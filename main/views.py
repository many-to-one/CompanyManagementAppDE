from django.shortcuts import render, redirect
from .models import Work
from django.http import HttpResponse

from users.models import CustomUser
def index(request):
    return render(request, "home.html")


def userWork(request, pk):
    if request.method == 'POST':
        date = request.POST.get('date')
        timestart = request.POST.get('timestart')
        timefinish = request.POST.get('timefinish')
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
        work.work_object = work_object
        work.work_type = work_type
        work.coffee_food = coffee_food
        work.prepayment = prepayment
        work.fuel = fuel
        work.phone_costs = phone_costs
        work.user.add(user)
        work.save()
        print(date, timestart, timefinish)
        # return redirect(request, 'home')
    user = CustomUser.objects.get(id=pk)
    context = {'user': user}
    return render(request, 'user_work.html', context)
