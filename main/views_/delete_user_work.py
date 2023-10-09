from django.shortcuts import redirect, render
from ..models import Work


def deleteUserWork(request, work_pk):

    try:
        work = Work.objects.get(id=work_pk)
        work.delete()
        return redirect('success_delete_user_work', work.date)
    except Exception as e:
        error = f'Wystąpił błąd: {e}'
        return render(request, 'error.html', {'error': error})
    

def success_delete_user_work(request, work_date):
    return render(request, 'success_delete_user_work.html', {'work_date': work_date})


def deleteListUserWorkQuestion(request):
    return render(request, 'deleteListUserWorkQuestion.html')


def deleteListUserWork(request):
    marked = request.session.get('marked', [])
    try:
        Work.objects.filter(id__in=marked).delete()
        return render (request, 'success_delete_list_user_work.html')
    except Exception as e:
        error = f'Wystąpił błąd: {e}'
        return render(request, 'error.html', {'error': error})
