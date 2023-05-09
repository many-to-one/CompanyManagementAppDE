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
        timefinish = request.POST.get('work_object')
        timefinish = request.POST.get('work_type')
        timefinish = request.POST.get('coffee_food')
        timefinish = request.POST.get('fuel')
        timefinish = request.POST.get('prepayment')
        timefinish = request.POST.get('phone_costs')
        user = CustomUser.objects.get(id=pk)
        work = Work.objects.create()
        work.date = date
        work.timestart = timestart
        work.timefinish = timefinish
        work.user.add(user)
        work.save()
        print(date, timestart, timefinish)
        # return redirect(request, 'home')
    user = CustomUser.objects.get(id=pk)
    context = {'user': user}
    return render(request, 'user_work.html', context)
