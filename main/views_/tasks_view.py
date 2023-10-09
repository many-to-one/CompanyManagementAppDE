from datetime import datetime
from django.shortcuts import render, get_object_or_404
from ..tasks import *
from ..models import (
    WorkObject, 
    Task,
    )
from django.http import JsonResponse
import ast


def task(request):
    if request.method == 'GET':
        user_pk = request.GET.get('user')
        work_object_pk = request.GET.get('work_object')
        user = get_object_or_404(CustomUser, id=int(user_pk))
        work_object = get_object_or_404(WorkObject, id=int(work_object_pk))
        print('UW ------------------------------------ ', user_pk, user, work_object)
        try:
            tasks = Task.objects.filter(
                user=user,
                work_object=work_object,
                ).order_by('date_obj')
            print('TASKS ------------------------------------ ', tasks)
            tasks_list = tasks.values()
        except Exception as e:
            return render(request, 'error.html',
                          context={'error': e})
        response = {
            'tasks_list': list(tasks_list),
            }
        print('RESPONSE ------------------------------------ ', response)
    return JsonResponse(response)
    

def new_task(request):

    pl_month = {
        'Jan': 'Sty',
        'Feb': 'Lut',
        'Mar': 'Mar',
        'Apr': 'Kwi',
        'May': 'Maj',
        'Jun': 'Cze',
        'Jul': 'Lip',
        'Aug': 'Sie',
        'Sep': 'Wrz',
        'Oct': 'Paź',
        'Nov': 'Lis',
        'Dec': 'Gru',
    }

    if request.method == 'POST':
        date = request.POST.get('date')
        user_pk = request.POST.get('user')
        work_object_pk = request.POST.get('work_object')
        content = request.POST.get('content')
        user = get_object_or_404(CustomUser, id=int(user_pk) )
        work_object = get_object_or_404(WorkObject, id=int(work_object_pk))
        print('user ------------------------- ', user_pk, user)
        # locale.setlocale(locale.LC_TIME, 'pl_PL')  # Polish locale not work in Container

        date = datetime.strptime(date, '%Y-%m-%d') # Ex: '2023-07-07'
        formatted_date = date.strftime('%d %b %Y') # Ex: '07 lipiec 2023'
        print('pl_month[formatted_date[2:-4].strip()],', pl_month[formatted_date[2:-4].strip()],)

        try:
            newTask = Task(
                date_obj=date,
                date=formatted_date,
                abbreviated_month=pl_month[formatted_date[2:-4].strip()],
                user=user,
                username=user.username,
                work_object=work_object,
                content=content,
            )
            newTask.save()
            print('new_task_month', newTask.abbreviated_month)
        except Exception as e:
            return render(request,
                          'error.html',
                          context={'error': f'Wystąpił błąd przy utworzeniu nowego zadania: {e}'})
        response_data = {
            'date': date,
            'user': user.username,
            'work_object': work_object.id,
            'content': content,
            'newTask': newTask.id,
        }
    return JsonResponse(response_data)


def taskQuantity(request):
    if request.method == 'GET':
        user = request.user
        if user.is_superuser:
            try:
                tasks = Task.objects.filter(
                    done=False
                )
            except Exception as e:
                response = {
                    'message': str(e)
                }
        else:
            try:
                tasks = Task.objects.filter(
                    user=user,
                    done=False
                )
            except Exception as e:
                response = {
                    'message': str(e)
                }

        response = {
            'count': tasks.count()
        }
        print('TASKCOUNT', tasks.count())
    return JsonResponse(response)


def getTask(request):
    if request.method == 'GET':
        pk = request.GET.get('pk')
        try:
            task = Task.objects.filter(
                id=int(pk)
                )
            task.update(done=True)
            response = {
                'message': 'ok'
            }
        except Exception as e:
            response = {
                'message': str(e)
            }
    return JsonResponse(response)


def doneTask(request):
    response = {}
    if request.method == 'POST':
        pk = request.POST.get('pk')
        try:
            task = Task.objects.get(id=int(pk))
            if task.done == False:
                task.done = True
            else:
                task.done = False
            task.save()
            response = {
                'message': task.done
            }
        except Task.DoesNotExist:
            response = {
                'message': 'error: Task does not exist'
            }
        except Exception as e:
            response = {
                'message': 'error: ' + str(e)
            }
    else:
        response = {
            'message': 'error: Invalid request method'
        }
    return JsonResponse(response)


def deleteTaskQuestion(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        print('PK !!!!!!!!!', pk)
        try:
            if pk.startswith('['):
                # Extract the task IDs with ast
                ids = ast.literal_eval(pk)
                tasks = Task.objects.filter(id__in=ids)
                if tasks.exists():
                    response = {
                        'message': 'ok'
                    }
                else:
                    response = {
                        'message': 'Zadania nie istnieje'
                    }
            else:
                # Assume pk is a single id (when it's not a JSON-encoded array)
                task = Task.objects.get(id=int(pk))
                if task is not None:
                    response = {
                        'message': 'ok'
                    }
                else:
                    response = {
                        'message': 'Zadania nie istnieje'
                    }
        except Exception as e:
            response = {
                'message': str(e) 
            }
    return JsonResponse(response)



def deleteTask(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        try:
            task = Task.objects.get(id=int(pk))
            task.delete()
            response = {
                'message': pk
            }
        except Exception as e:
            response = {
                'message': e
            }
    return JsonResponse(response)


def deleteAllDoneTasksQuestion(request):
    if request.method == 'GET':
        try:
            Task.objects.filter(done=True).delete()
            response = {
                'message': 'ok',
                'content': 'Wszystkie zakończone zadania zostały usunięte'
            }
        except Exception as e:
            response = {
                'message': e
            }
    return JsonResponse(response)