from datetime import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from ..utils import months_pl_shorts
from ..tasks import *
from ..models import (
    WorkObject, 
    )
from django.contrib import messages
from users.models import CustomUser


#**********************************************************************************************************************#
#************************************************** CREATE WORK OBJECT ************************************************#
#**********************************************************************************************************************#


def createWorkObject(request):
    users = CustomUser.objects.all()
    works = [work.name for work in WorkObject.objects.all()]

    if request.method == 'POST':
        workname = request.POST.get('workname')
        timestart = request.POST.get('timestart')
        timefinish = request.POST.get('timefinish')
        if workname in works:
            messages.warning(request, 'Obiekt z podobną nazwą już istnieje lub jest w historii raportów, wprowadź inną')
            return redirect(reverse('create_work_object'))

        if timestart and timefinish:
            # Parse the input dates
            parsed_start = datetime.strptime(timestart, '%Y-%m-%d').date()
            parsed_finish = datetime.strptime(timefinish, '%Y-%m-%d').date()

            # Format the parsed date into "Day Month Year" format
            formatted_start = parsed_start.strftime('%d %b %Y')
            formatted_finish = parsed_finish.strftime('%d %b %Y')

        if workname != '':
            try:
                work = WorkObject.objects.create()
                work.name = workname
                if timestart and timefinish:
                    work.timestart = months_pl_shorts(formatted_start)
                    work.timefinish = months_pl_shorts(formatted_finish)
                users_list = request.POST.getlist('users')
                work.user.add(*users_list)
                work.save()
            except Exception as e:
                error = f'Wystąpił błąd: {e}, nie można utworzyć object'
                return render(request, 'error.html', {'error': error})
            return redirect('work_objects')
        else:
            messages.warning(request, 'Wpisz nazwę obiekta')
            return redirect(reverse('create_work_object'))
        
    context = {
        'users': users,
    }
    return render(request, 'create_work_object.html', context)


def updateWorkObject(request, pk):

    work = WorkObject.objects.get(id=pk)

    if request.method == 'POST':
        timestart = request.POST.get('timestart')
        timefinish = request.POST.get('timefinish')

        if timestart:
            parsed_start = datetime.strptime(timestart, '%Y-%m-%d').date()
            formatted_start = parsed_start.strftime('%d %b %Y')

            try:
                work.timestart = months_pl_shorts(formatted_start)
                work.save()
                return redirect('work_objects')
            except Exception as e:
                error = f'Wystąpił błąd: {e}, nie można edytować object'
                return render(request, 'error.html', {'error': error})
            
        if timefinish:
            parsed_finish = datetime.strptime(timefinish, '%Y-%m-%d').date()
            formatted_finish = parsed_finish.strftime('%d %b %Y')

            try:
                work.timefinish = months_pl_shorts(formatted_finish)
                work.save()
                return redirect('work_objects')
            except Exception as e:
                error = f'Wystąpił błąd: {e}, nie można edytować object'
                return render(request, 'error.html', {'error': error})

        if timestart and timefinish:
            # Parse the input dates
            parsed_start = datetime.strptime(timestart, '%Y-%m-%d').date()
            parsed_finish = datetime.strptime(timefinish, '%Y-%m-%d').date()

            # Format the parsed date into "Day Month Year" format
            formatted_start = parsed_start.strftime('%d %b %Y')
            formatted_finish = parsed_finish.strftime('%d %b %Y')

            try:
                work.timestart = months_pl_shorts(formatted_start)
                work.timefinish = months_pl_shorts(formatted_finish)
                work.save()
                return redirect('work_objects')
            except Exception as e:
                error = f'Wystąpił błąd: {e}, nie można edytować object'
                return render(request, 'error.html', {'error': error})
        
    context = {
        'work': work,
    }
    return render(request, 'update_work_object.html', context)