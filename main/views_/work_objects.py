from datetime import datetime
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from ..utils import months_pl_shorts
from ..tasks import *
from ..models import WorkObject
from django.core.paginator import Paginator


#**********************************************************************************************************************#
#*************************************************** ALL WORK OBJECTS *************************************************#
#**********************************************************************************************************************#


def WorkObjects(request):
    if request.user.is_superuser:
        all_work_objects = WorkObject.objects.all().order_by('timefinish')
        work_objects = WorkObject.objects.filter(
            ).order_by('timefinish').exclude(status='Zakończone')
    else:
        all_work_objects = WorkObject.objects.filter(
            user=request.user
        ).order_by('id').exclude(status='Zakończone')
        work_objects = WorkObject.objects.filter(
            user=request.user,
        ).order_by('id').exclude(status='Zakończone')
    work_objects_list = all_work_objects.values_list('name', flat=True)
    work_objects_status_list = all_work_objects.values_list('status', flat=True)
    work_objects_status = set(work_objects_status_list)

    # Get the current date
    current_date = datetime.now().date()
    formatted_date = months_pl_shorts(current_date.strftime('%d %b %Y'))

    for wo in all_work_objects:
        if int(wo.timefinish[:2]) - int(formatted_date[:2]) <= 1 and wo.status == 'Aktywne':
            wo.deadline = True
        elif int(wo.timefinish[:2]) - int(formatted_date[:2]) >= 0:
            wo.remaining_time = int(wo.timefinish[:2]) - int(formatted_date[:2])
            wo.save()
                  
        if wo.timefinish == formatted_date and wo.status == 'Aktywne':
            wo.status = 'Spóźnione'
            wo.deadline = True
            wo.save()

        if wo.status == 'Zakończone':
            wo.finished = True
            wo.save()

    if request.method == 'POST':
        timestart = request.POST.get('timestart')
        select = request.POST.get('object')
        status = request.POST.get('status')
        fromEnd = request.POST.get('fromEnd')
        if select == 'Wszystkie objekty' and status == None or status == 'Wszystkie objekty' and select == None:
            work_objects = WorkObject.objects.all()
        elif status == None:
            work_objects = WorkObject.objects.filter(name=select)
        elif select == None:
            work_objects = WorkObject.objects.filter(status=status)
        if fromEnd:
            work_objects = work_objects.order_by('-remaining_time')
            print('remain ------------------', fromEnd)
    
    # if request.method == 'GET':
    # if 'remain' in request.GET:
    #     work_objects = WorkObject.objects.all().order_by('-remaining_time')

    paginator = Paginator(work_objects, 10) 
    page_number = request.GET.get('page')
    work_objects = paginator.get_page(page_number)
    context = {
        'work_objects': work_objects,
        'work_objects_list': work_objects_list,
        'work_objects_status': work_objects_status,
    }

    return render(request, 'work_objects.html', context)


def changeStatusWorkObject(request, pk):
    wo = get_object_or_404(WorkObject, id=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        wo.status = status
        wo.save()

        response = {
            'status': wo.status
        }

    return JsonResponse(response)


def deleteWorkObjectQuestion(request, work_object_pk):
    work_object = get_object_or_404(WorkObject, id=work_object_pk)
    context = {
        'work_object': work_object,
    }
    return render (request, 'deleteWorkObjectQuestion.html', context)


def deleteWorkObject(request, work_object_pk):   
    try:
        work_object = get_object_or_404(WorkObject, id=work_object_pk)
        work_object.delete()
        context = {
            'work_object_name': work_object.name
        }
        return render(request, 'success_delete_workobject.html', context)
    except Exception as e:
        error = f'Wystąpił błąd: {e}'
        return render(request, 'error.html', {'error': error})