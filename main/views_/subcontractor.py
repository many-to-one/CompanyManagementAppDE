from django.shortcuts import get_object_or_404
from ..tasks import *
from ..models import (
    WorkObject, 
    Subcontractor,
    )
from django.http import JsonResponse


def addSubcontractor(request, pk):
    work_object = get_object_or_404(WorkObject, id=pk)
    if request.method == 'POST':
        subcontractor = request.POST.get('subcontractor')
        print('subcontractor --------------', subcontractor)
        time = request.POST.get('time')
        price = request.POST.get('price')
        sub = Subcontractor(
            name=subcontractor,
            time=float(time),
            price=float(price),
            sum = float(time) * float(price),
            work_object=work_object,
        )
        sub.save()
        work_object.total += sub.sum
        work_object.save()

        response = {
            'total': sub.sum
        }
    
    return JsonResponse(response)


def deleteSubcontractor(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        subcontractor = get_object_or_404(Subcontractor, id=int(pk))
        subcontractor.delete()
        response = {
            'status': f'{subcontractor.id} was deleted'
        }

    return JsonResponse(response)