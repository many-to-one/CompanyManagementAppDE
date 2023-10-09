from django.shortcuts import render
from ..models import Work


def deleteUserWorkQuastion(request, work_pk):
    marked = request.session.get('marked')
    try:
        work = Work.objects.get(id=work_pk)
    except Exception as e:
        error = f'Wystąpił błąd: {e}'
        return render(request, 'error.html', {'error': error})

    context = {
        'work': work,
        'marked': marked,
    }
    return render(request, 'deleteUserWorkQuastion.html', context)