import ast
from datetime import datetime, timedelta, date
import json
from django.core import serializers
import os
import re
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .utils import months_pl_shorts
from .tasks import *
from .models import (
    Documents,
    MessageCount,
    MessageCountUser,
    VacationRequest, 
    Vacations, 
    Work, 
    WorkObject, 
    WorkType, 
    Message, 
    IsRead, 
    Task,
    Subcontractor,
    )
from django.http import JsonResponse
from django.db.models import Sum, F, Prefetch
from django.contrib import messages
from users.models import CustomUser
from django.core.paginator import Paginator
import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse


def index(request):
    return render(request, "home.html")


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


#**********************************************************************************************************************#
#*************************************************** WORK OBJECT VIEW *************************************************#
#**********************************************************************************************************************#

def workObjectView(request, **kwargs):

    allusers = CustomUser.objects.all()
    work_object = WorkObject.objects.get(id=kwargs['pk'])
    users = work_object.user.all()
    messages = Message.objects.filter(
        work_object=work_object,
       )

    subcontractors = work_object.subcontractor.all()
    subcontractors_sum = Subcontractor.objects.filter(
       work_object=work_object 
    ).aggregate(
        subcontractors_sum=Sum('sum')
    )
    print('work_object.id --------------------', work_object.id)
    print('work_object.name --------------------', work_object.name)
    print('work_object.total --------------------', work_object.total)

    ##############################
    ### Totals for work_object ###

    total_fields = {
        'total_material_costs': 'material_costs',
        'total_coffee_food': 'coffee_food',
        'total_fuel': 'fuel',
        'total_prepayment': 'prepayment',
        'total_phone_costs': 'phone_costs',
        'total_payment': 'payment',
        'total_sum_time_sec': 'sum_time_sec',
        'total_sum_over_time_sec': 'sum_over_time_sec'
    }

    totals = {}
    for field_name, field in total_fields.items():
        total = Work.objects.filter(
            work_object=work_object.id
            ).aggregate(
            total=Sum(field)
            )['total']
        totals[field_name] = total

    # Calculate total work time in this object
    if totals['total_sum_time_sec']:
        ### total_sum_time_sec => hours:minutes ###
        total_hours = totals['total_sum_time_sec'] // 3600
        total_sec = totals['total_sum_time_sec'] % 3600
        total_min = total_sec // 60
        total_work_time = f'{int(total_hours)}:{int(total_min)}' 
    else:
        total_work_time = '0:00'
    if totals['total_sum_over_time_sec']:
        ### total_sum_over_time_sec => hours:minutes ###
        total_hours = totals['total_sum_over_time_sec'] // 3600
        total_sec = totals['total_sum_over_time_sec'] % 3600
        total_min = total_sec // 60
        if total_min < 10 or total_min == 0.0:
            total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
        else:
            total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_over_time = '0:00'
    ### End Totals for sorted_from ###
    ################################## 
    
    ## Add new user to the object & make chat with all users belong to it
    if request.method == 'POST':
        ## Add new user in work object
        if 'add_user' in request.POST:
            user = request.POST.get('user')
            if user == '':
                error = 'Nie wybrano żadnego użytkownika'
                return render(request, 'error.html', {'error': error})
            # add_user = CustomUser.objects.get(username=user)
            add_user = get_object_or_404(CustomUser, username=user)
            try:
                work_object.user.add(add_user)
                work_object.save()
            except Exception as e:
                return render(request, 
                              'error.html',
                              context={'error': f'Wystąpił błąd: użytkownika nie istnieje, {e}'}
                              )
            work_object = get_object_or_404(WorkObject, id=kwargs['pk'])
            users = work_object.user.all()

    total_lists = [
        totals['total_payment'],
        totals['total_phone_costs'],
        totals['total_fuel'],
        totals['total_coffee_food'],
        totals['total_material_costs'],
    ]

    if any(element is not None for element in total_lists):
        total = sum(total_lists)
    else:
        total = '0.00'
        totals['total_payment'] = '0.00'
        totals['total_prepayment'] = '0.00'
        totals['total_phone_costs'] = '0.00'
        totals['total_fuel'] = '0.00'
        totals['total_coffee_food'] = '0.00'
        totals['total_material_costs'] = '0.00'
    
    sub_sum = subcontractors.aggregate(total=Sum('sum'))['total']
    if sub_sum:
        work_object.total = sub_sum + float(total)
        work_object.save()
    else:
        work_object.total = float(total)
        work_object.save()

    context = {
        'current_time': datetime.now().strftime('%Y-%m-%d'),
        'messages': messages,
        'work_object': work_object,
        'users': users,
        'allusers': allusers,
        'total_material_costs': totals['total_material_costs'],
        'total_coffee_food': totals['total_coffee_food'],
        'total_fuel': totals['total_fuel'],
        'total_prepayment': totals['total_prepayment'],
        'total_phone_costs': totals['total_phone_costs'],
        'total_payment': totals['total_payment'],
        'total_work_time': total_work_time,
        'total': total,
        'subcontractors': subcontractors,
        'subcontractors_sum': subcontractors_sum['subcontractors_sum'],
    }
    return render(request, 'work_object.html', context)


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



def task(request):
    if request.method == 'GET':
        user_pk = request.GET.get('user')
        work_object_pk = request.GET.get('work_object')
        user = get_object_or_404(CustomUser, id=int(user_pk))
        work_object = get_object_or_404(WorkObject, id=int(work_object_pk))
        try:
            tasks = Task.objects.filter(
                user=user,
                work_object=work_object,
                ).order_by('date_obj')

            tasks_list = tasks.values()
        except Exception as e:
            return render(request, 'error.html',
                          context={'error': e})
        response = {
            'tasks_list': list(tasks_list),
            }
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


def deleteQuestionMessages(request):
    if request.method == 'GET':
        response = {'message': 'ok',}    
    return JsonResponse(response)    


def deleteAllMessagesWO(request):
    if request.method == 'POST':
        work_object = request.POST.get('work_object')
        print('work_object', work_object)
        try:
            messages = Message.objects.filter(work_object=work_object)
            if messages is not None:
                MessageCountUser.objects.all().delete()
                messages.delete()
                response = {
                    'message': 'ok',
                    'content': 'Wiadomości zostały usunięte'
                }
            else:
                response = {
                    'message': 'Nie ma żadnych wiadomości do usunięcia'
                }
        except Exception as e:
            response = {
                'message': e
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


def header(request):
    if request.method == 'GET':
        menu_ = ''
        if 'menu' in request.GET:
            # Handle GET request with data
            menu = request.GET.get('menu')
            if menu == 'active':
                menu_ = 'active'
            else:
                menu_ = 'inactive'
            response = {
                'menu': menu_
            }
            return JsonResponse(response)
        else:
            # Handle GET request without data
            if menu_ == 'active':
                response = {
                'menu': 'active'
                }
            else:
                response = {
                'menu': 'inactive'
                }
            return JsonResponse(response)


    

def schedule(request):
    user = request.user
    if user.is_superuser:
        try:
            tasks = Task.objects.all().prefetch_related('work_object')
            done_tasks = Task.objects.filter(done=True).only('id')
            task_ids = list(done_tasks.values_list('id', flat=True))
            print('done_tasks!!!!!!!!!', task_ids)
            # done_tasks_json = serializers.serialize('json', done_tasks)
        except Exception as e:
            return render(request,
                          'error.html',
                          context={'error': f'Wystąpił błąd (Grafik): {e}'})
    else:
        try:
            tasks = Task.objects.filter(
                user=user
            )
            done_tasks = Task.objects.filter(done=True).only('id')
            task_ids = list(done_tasks.values_list('id', flat=True))
        except Exception as e:
            return render(request,
                          'error.html',
                          context={'error': f'Wystąpił błąd (Grafik): {e}'})

    # This code stoped work in Docker:
    # try:
    #     locale.setlocale(locale.LC_TIME, 'pl_PL')
    # except locale.Error as e:
    #     print(f"Error setting locale: {e}")
    # else:
    #     print("Locale set successfully.")

    # Abbreviated_month PL dict
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

    if tasks:
        for task in tasks:
            date_obj = datetime.strptime(task.date, '%d %b %Y')
            formatted_date = date_obj.strftime('%d %b %Y')
            # .strip() Remove leading and trailing whitespaces from the formatted_date
            task.date_obj = date_obj
            task.abbreviated_month = pl_month[formatted_date[2:-4].strip()]
            task.save()
        context = {
            'tasks': tasks.order_by('date_obj'),
        }
        if done_tasks:
            context = {
                'tasks': tasks.order_by('date_obj'),
                'done_tasks': task_ids,
            }
    else:
        context = {
                'no_tasks': 'Na razie nie ma żadnych zadań',
            }

    return render(request, 'shedule.html', context)


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


def deleteUserFromObjectQuestion(request, user_pk, work_object_pk):
    try:
        user_query = CustomUser.objects.filter(id=user_pk).values_list('username')
        user = [user[0] for user in user_query]
    except Exception as e:
            return render(request,
                          'error.html',
                          context={'error': f'Wystąpił błąd: {e}'})
    context = {
        'user': user[0],
        'user_pk': user_pk,
        'work_object_pk': work_object_pk
    }
    return render (request, 'deleteUserFromObjectQuestion.html', context)


def deleteUserFromObject(request, user_pk, work_object_pk):
    user = get_object_or_404(CustomUser, id=user_pk)
    work_object = get_object_or_404(WorkObject, id=work_object_pk)
    try:
        work_object.user.remove(user)
        work_object.save()
        context = {
        'username': user.username,
        'work_object': work_object,
        }
        return render(request, 'success_delete_user_from_workobject.html', context)
    except Exception as e:
        error = f'Wystąpił błąd: {e}'
        return render(request, 'error.html', {'error': error})


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


from django.template import Context, Template
def showCount(request, work_object_pk):
    user = request.user
    if request.method == 'GET':
        work_object = get_object_or_404(WorkObject, id=work_object_pk)
        template = Template("{% load messages %} {% messages_quantity user work_object %}")
        context = Context({'user': user, 'work_object': work_object})
        print('CALLED !!!!!!!!!!!!!!!!!!!!!!')
        count = template.render(context)
        print('COUNT !!!!!!!!!!!!!!!!!!!!!!', count)
        response = {'count': count,}
    return JsonResponse(response)


def showCountAll(request):
    if request.method == 'GET':
        username = request.user.username
        if request.user.is_authenticated:
            template = Template("{% load messages %} {% all_messages_quantity username %}")
            context = Context({'username': username,})
            count = template.render(context)
        else:
            count = 0
        response = {'count': count,}
    return JsonResponse(response)


from django.db.models import Q

def showMessageHistory(request, pk):
    if request.method == 'GET':
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        work_object = get_object_or_404(WorkObject, id=pk)
        username = request.user.username

        # Update is_read flag for messages
        try:
             # Last 5 messages in current work object
            read_messages = Message.objects.filter(work_object=work_object).order_by('id')

            # All messages in current object for user who open the chat
            read_filter = Q(message__in=read_messages) & Q(username=username)

            # Count of unread messages only for recipients
            unread_messages = Message.objects.filter(
                work_object=work_object, 
                isread__is_read=False # Calling the child model - IsRead
                )

            # Finding the sender username of unread messages
            sender = ''
            for um in unread_messages:
                sender = um.sender.username

            # Count of unread messages
            unread_messages_count = IsRead.objects.filter(
                work_object=work_object,
                is_read=False,
            ).exclude(
                username=sender
            ).count()

            # if count of unread messages > 0 the message will be
            # marked - unread - for sender after he will sent it
            if unread_messages_count > 0:
                # Marke message - is_read - for first user who
                # has read the message, exlude sender
                read_by_someone = IsRead.objects.filter(
                        work_object=work_object, 
                        message__in=unread_messages,
                        username=username,
                    ).exclude(
                        username=sender
                    ).update(
                        is_read=True
                    )

                # If somebody has read the message, the message
                # will be marked - is_read - for sender
                if read_by_someone:
                    IsRead.objects.filter(
                            work_object=work_object, 
                            username=sender
                        ).update(
                            is_read=True
                        )
            else:
                # All messages in current work object marks like is_read
                IsRead.objects.filter(read_filter).update(is_read=True)
            messages = list(read_messages.values())

        except Exception as e:
            error = f'Wystąpił błąd: {e}, nie można wyświetlić wiadomości'
            return render(request, 'error.html', {'error': error})

        for message in messages:
            is_read = IsRead.objects.filter(message_id=message['id'], username=username).first()
            message['is_read'] = is_read.is_read if is_read else False

        response = {
            'user': username,
            'messages': messages,
            'mess_count': read_messages.count(),
            'current_time': current_time,
            'status': 'ok',
        }

        return JsonResponse(response)



def chat(request, pk):
    if request.method == 'GET':
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        work_object = get_object_or_404(WorkObject, id=pk)
        username = request.user.username

        # Update is_read flag for messages
        try:
            # messages_results = update_is_read_flag.delay(pk, username)
            # messages = messages_results.get()

             # Last 20 messages in current work object
            read_messages = Message.objects.filter(work_object=work_object).order_by('-id')[:20]
            # mess_count

            # All messages in current object for user who open the chat
            read_filter = Q(message__in=read_messages) & Q(username=username)

            # Count of unread messages only for recipients
            unread_messages = Message.objects.filter(
                work_object=work_object, 
                isread__is_read=False # Calling the child model - IsRead
                )

            # Finding the sender username of unread messages
            sender = ''
            for um in unread_messages:
                sender = um.sender.username

            # Count of unread messages
            unread_messages_count = IsRead.objects.filter(
                work_object=work_object,
                is_read=False,
            ).exclude(
                username=sender
            ).count()

            # if count of unread messages > 0 the message will be
            # marked - unread - for sender after he will sent it
            if unread_messages_count > 0:
                # Marke message - is_read - for first user who
                # has read the message, exlude sender
                read_by_someone = IsRead.objects.filter(
                        work_object=work_object, 
                        message__in=unread_messages,
                        username=username,
                    ).exclude(
                        username=sender
                    ).update(
                        is_read=True
                    )

                # If somebody has read the message, the message
                # will be marked - is_read - for sender
                if read_by_someone:
                    IsRead.objects.filter(
                            work_object=work_object, 
                            username=sender
                        ).update(
                            is_read=True
                        )
            else:
                # All messages in current work object marks like is_read
                IsRead.objects.filter(read_filter).update(is_read=True)
            messages = list(read_messages.values())[::-1] # [::-1] to show last reversed messages

        except Exception as e:
            error = f'Wystąpił błąd: {e}, nie można wyświetlić wiadomości'
            return render(request, 'error.html', {'error': error})
        
        # Add 'is_read' field to each message dictionary
        # try:
        #     # messages_results = get_messages.delay(pk, username, current_time)
        #     # messages = messages_results.get()
        #     print('MESSAGES !!!!!!!!!!!!!!!', messages)
        # except Exception as e:
        #     error = f'Wystąpił błąd: {e}, nie można wyświetlić wiadomości'
        #     return render(request, 'error.html', {'error': error})
        # print('MESSAGES !!!!!!!!!!!!!!!', messages)
        for message in messages:
            is_read = IsRead.objects.filter(message_id=message['id'], username=username).first()
            message['is_read'] = is_read.is_read if is_read else False

        response = {
            'user': username,
            'messages': messages,
            'mess_count': read_messages.count(),
            'current_time': current_time,
            'status': 'ok',
        }

        return JsonResponse(response)
    
    if request.method == 'POST':
        work_object = get_object_or_404(WorkObject, id=pk)
        try:
            users = CustomUser.objects.filter(workobject__id=pk)
        except Exception as e:
            error = f'Wystąpił błąd: {e}'
            return render(request, 'error.html', {'error': error})
        r_user = request.user
        content = request.POST.get('txt')
        user = request.POST.get('user')

        # Create the new message
        try:
            new_message = Message.objects.create(
                name=user,
                sender=r_user,
                content=content,
                day=f"{datetime.now().strftime('%d %b %Y')} ",
                time=f'{datetime.now().hour}:{datetime.now().minute}',
                work_object=work_object,
                for_sender_is_read=True,
            )

            subject = 'Adest GmbH ERP'
            url = f'https://www.workmeneger.pl/work_object/{work_object.id}/'
            message = f'Wiadomość w czacie z obiektu: {work_object.name}, <a href="{url}">sprawdź</a>'
            html_message = f'<p>{message}</p>'
            plain_message = f'{message}'
            email_from = settings.EMAIL_HOST_USER

            # The list of user's emails whose are offline to send them alert about the new message 
            recipient_list = [u.email for u in users if u.email != r_user.email and u.is_logged == False]

            # celery task for sending email
            mail_message(subject, plain_message, email_from, recipient_list, html_message)

            # new_message_results = create_message.delay(pk, r_user, content, user)
            # new_message = new_message_results.get()
        except Exception as e:
            error = f'Wystąpił błąd: {e}, nie można wysłać wiadomości'
            return render(request, 'error.html', {'error': error})

        # Create IsRead instances for all users
        is_read_list = [
            IsRead(
                message=new_message,
                username=user.username,
                work_object=work_object,
            )
            for user in users
        ]
        IsRead.objects.bulk_create(is_read_list)

        response = {
            'new_message_id': new_message.id,
        }
        return JsonResponse(response)
    

# This function checks if the users has a new message, exclude the sender
def chek_messages_user(request):
    user = request.user
    if request.method == 'GET':
        new_mess = Message.objects.all().order_by('-id').values('content', 'work_object').first()
        count_mess = Message.objects.all().exclude(sender=user).count()
        print('COUNT_MESS --------------', count_mess)
        messageCount, created = MessageCountUser.objects.get_or_create(user=user)
        if count_mess > messageCount.message_count:
            messageCount.message_count = count_mess
            messageCount.save()
            print('CHECK_MESS_COUNT BOLSZE ---------------------', count_mess, messageCount.message_count) 
            response = {
                    'message': True,
                    'new_mess': new_mess,
                    # 'chat_id': new_mess['work_object']
                }
        elif count_mess < messageCount.message_count:
            messageCount.message_count = count_mess
            messageCount.save()
            print('CHECK_MESS_COUNT MENSZE ---------------------', count_mess, messageCount.message_count) 
            response = {
                    'message': 1,
                    'user': user.is_logged,
                }
        else:
            print('CHECK_MESS_COUNT ROWNO --------------------', count_mess, messageCount.message_count) 
            response = {
                    'message': False,
                    'user': user.is_logged,
                }


    return JsonResponse(response)
   

# This function checks if there is a new message in the chat of
# the current work object by checking theirs count. If there is a 
# new message the function return True and the JS function in 
# work_object.html refreash the chat to show all messages, with 
# the new one.
def chek_messages(request, pk):
    user = request.user
    if request.method == 'GET':
        work_object = get_object_or_404(WorkObject, id=pk)
        count_mess = work_object.objekt.count()
        # print('COUNT_MESS --------------', count_mess)
        # print('WORK_OBJECT --------------', work_object)
        messageCount, created = MessageCount.objects.get_or_create(
            user=user,
            work_object=work_object,
        )
        if count_mess > messageCount.message_count:
            messageCount.message_count = count_mess
            messageCount.save()
            # print('CHECK_MESS_COUNT BOLSZE ---------------------', count_mess, messageCount.message_count) 
            response = {
                    'message': True
                }
        elif count_mess < messageCount.message_count:
            messageCount.message_count = count_mess
            messageCount.save()
            # print('CHECK_MESS_COUNT MENSZE ---------------------', count_mess, messageCount.message_count) 
            response = {
                    'message': 1
                }
        else:
            # print('CHECK_MESS_COUNT ROWNO --------------------', count_mess, messageCount.message_count) 
            response = {
                    'message': False
                }


    return JsonResponse(response)


def deleteMessConf(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        try:
            mess = Message.objects.get(id=pk)
            mess.delete()
            response = {'message': f'message{pk} was deleted!'}
        except Exception as e:
            return render(request, 'error.html', context={'error': e})
        
        return JsonResponse(response)


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


#**********************************************************************************************************************#
#************************************************* USER CREATE HIS WORK ***********************************************#
#**********************************************************************************************************************#

def userWork(request, pk):
    if request.method == 'POST':
        date = request.POST.get('date')
        timestart = request.POST.get('timestart')
        timefinish = request.POST.get('timefinish')
        timestart_break1 = request.POST.get('timestart_break1')
        timefinish_break1 = request.POST.get('timefinish_break1')
        timestart_break2 = request.POST.get('timestart_break2')
        timefinish_break2 = request.POST.get('timefinish_break2')
        work_object = request.POST.get('work_object')
        work_type = request.POST.get('work_type')
        material_costs = request.POST.get('material_costs')
        coffee_food = request.POST.get('coffee_food')
        fuel = request.POST.get('fuel')
        prepayment = request.POST.get('prepayment')
        phone_costs = request.POST.get('phone_costs')

        if date == '':
            messages.warning(request, 'Wybierz date!')
            return redirect(reverse('user_work', kwargs={'pk': pk}))
        if timestart == '':
            messages.warning(request, 'Zaznacz początek czasu pracy!')
            return redirect(reverse('user_work', kwargs={'pk': pk}))
        if timefinish == '':
            messages.warning(request, 'Zaznacz koniec czasu pracy!')
            return redirect(reverse('user_work', kwargs={'pk': pk}))
        if work_object == None:
            messages.warning(request, 'Wybierz Obiekt pracy!')
            return redirect(reverse('user_work', kwargs={'pk': pk}))

        ### Here we need to make str(date) => int(date) to sum it ###
        year, month, day = date.split('-')
        start_hr, start_min = timestart.split(':') 
        finish_hr, finish_min = timefinish.split(':') 
        start = datetime(int(year), int(month), int(day), int(start_hr), int(start_min))
        end = datetime(int(year), int(month), int(day), int(finish_hr), int(finish_min))

        #BREAKFAST
        if timestart_break1 and timefinish_break1:
            start_hr_break1, start_min_break1 = timestart_break1.split(':')  
            finish_hr_break1, finish_min_break1 = timefinish_break1.split(':') 
            start_break1 = datetime(int(year), int(month), int(day), int(start_hr_break1), int(start_min_break1))
            end_break1 = datetime(int(year), int(month), int(day), int(finish_hr_break1), int(finish_min_break1))
            dif_break1 = end_break1 - start_break1 

            dif_hours_break1 = dif_break1.seconds // 3600
            dif_sec_break1 = dif_break1.seconds % 3600
            dif_min_break1 = dif_sec_break1 // 60
            if dif_min_break1 < 10 or dif_min_break1 == 0:
                bt = f'{dif_hours_break1}:0{dif_min_break1}'
            else:
                bt = f'{dif_hours_break1}:{dif_min_break1}'

            # Work time in seconds without break
            diff = end - start - dif_break1 
            # print('dif_break1 -------------- ', diff)

        #LANCH
        elif timestart_break2 and timefinish_break2:
            start_hr_break2, start_min_break2 = timestart_break2.split(':')  
            finish_hr_break2, finish_min_break2 = timefinish_break2.split(':') 
            start_break2 = datetime(int(year), int(month), int(day), int(start_hr_break2), int(start_min_break2))
            end_break2 = datetime(int(year), int(month), int(day), int(finish_hr_break2), int(finish_min_break2))
            dif_break2 = end_break2 - start_break2

            dif_hours_break2 = dif_break2.seconds // 3600
            dif_sec_break2 = dif_break2.seconds % 3600
            dif_min_break2 = dif_sec_break2 // 60
            if dif_min_break2 < 10 or dif_min_break2 == 0:
                bt = f'{dif_hours_break2}:0{dif_min_break2}'
            else:
                bt = f'{dif_hours_break2}:{dif_min_break2}'

            # Work time in seconds without break
            diff = end - start - dif_break2
            # print('dif_break2 --------------', diff)

        elif timestart_break1 and timefinish_break1 and timestart_break2 and timefinish_break2:
            start_hr_break1, start_min_break1 = timestart_break1.split(':')  
            finish_hr_break1, finish_min_break1 = timefinish_break1.split(':') 
            start_break1 = datetime(int(year), int(month), int(day), int(start_hr_break1), int(start_min_break1))
            end_break1 = datetime(int(year), int(month), int(day), int(finish_hr_break1), int(finish_min_break1))
            dif_break1 = end_break1 - start_break1 
            start_hr_break2, start_min_break2 = timestart_break2.split(':')  
            finish_hr_break2, finish_min_break2 = timefinish_break2.split(':') 
            start_break2 = datetime(int(year), int(month), int(day), int(start_hr_break2), int(start_min_break2))
            end_break2 = datetime(int(year), int(month), int(day), int(finish_hr_break2), int(finish_min_break2))
            dif_break2 = end_break2 - start_break2

            dif_hours_break2 = dif_break1.seconds // 3600
            dif_sec_break1 = dif_break1.seconds % 3600
            dif_min_break1 = dif_sec_break1 // 60
            if dif_min_break1 < 10 or dif_min_break1 == 0:
                bt = f'{dif_hours_break1}:0{dif_min_break1}'
            else:
                bt = f'{dif_hours_break1}:{dif_min_break1}'

            # Work time in seconds without break
            diff = end - start - dif_break1 - dif_break2
            # print('dif_break1 + dif_break2 --------------', diff)

        else:
            # Work time in seconds without break
            diff = end - start 
            # print('without brak --------------', diff)

        # print('diff_diff --------------', diff)
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

        user = CustomUser.objects.get(id=pk)
        # work_object = WorkObject.objects.get(name=work_object)
        payment = (user.payment / 3600) * diff.seconds
        print('PAYMENT', payment, type(payment))
        try:
            work = Work.objects.create()
            work.date = date
            work.username = user.username
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
            work.material_costs = float(material_costs)
            work.coffee_food = float(coffee_food)
            work.prepayment = float(prepayment)
            work.fuel = float(fuel)
            work.phone_costs = float(phone_costs)
            payment_ = float(payment)
            work.payment = round(payment_, 2)
            if timestart_break1:
                work.timestart_break1 = timestart_break1
            if timefinish_break1:    
                work.timefinish_break1 = timefinish_break1
            if timestart_break2:
                work.timestart_break2 = timestart_break2
            if timefinish_break2:
                work.timefinish_break2 = timefinish_break2
            work.user.add(user)
            try:
                work.save()
            except Exception as e:
                error = f'Nie można zaraportować pracę z powodu błędu: {e}'
                return render(request, 'error.html',
                              context={'error': error})
            return redirect('raports')
        except Exception as e:
            error = f'Nie można zaraportować pracę z powodu błędu: {e}'
            return render(request, 'error.html',
                          context={'error': error})

    work_objects = WorkObject.objects.filter(user__id=pk).only('name')
    return render(request, 'user_work.html',
                  context={'work_objects': work_objects})


#**********************************************************************************************************************#
#************************************************** UPDATE USER WORK **************************************************#
#**********************************************************************************************************************#

def updateUserWork(request, work_pk):
    print('work_pk----------------', work_pk)
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
        timestart_break1 = request.POST.get('timestart_break1')
        timefinish_break1 = request.POST.get('timefinish_break1')
        timestart_break2 = request.POST.get('timestart_break2')
        timefinish_break2 = request.POST.get('timefinish_break2')
        work_object = request.POST.get('work_object')
        work_type = request.POST.get('work_type')
        material_costs = request.POST.get('material_costs')
        coffee_food = request.POST.get('coffee_food')
        fuel = request.POST.get('fuel')
        prepayment = request.POST.get('prepayment')
        phone_costs = request.POST.get('phone_costs')


        if date == '':
            messages.warning(request, 'Wybierz date!')
            return redirect(reverse('update_user_work', kwargs={'work_pk': work_pk}))
        if timestart == '':
            messages.warning(request, 'Zaznacz początek czasu pracy!')
            return redirect(reverse('update_user_work', kwargs={'work_pk': work_pk}))
        if timefinish == '':
            messages.warning(request, 'Zaznacz koniec czasu pracy!')
            return redirect(reverse('update_user_work', kwargs={'work_pk': work_pk}))
        if work_object == None:
            messages.warning(request, 'Wybierz Obiekt pracy!')
            return redirect(reverse('update_user_work', kwargs={'work_pk': work_pk}))

        ### Here we need to make str(date) => int(date) to sum it ###
        year, month, day = date.split('-')
        start_hr, start_min = timestart.split(':') 
        finish_hr, finish_min = timefinish.split(':') 
        start = datetime(int(year), int(month), int(day), int(start_hr), int(start_min))
        end = datetime(int(year), int(month), int(day), int(finish_hr), int(finish_min))

        #BREAKFAST
        if timestart_break1 and timefinish_break1:
            start_hr_break1, start_min_break1 = timestart_break1.split(':')  
            finish_hr_break1, finish_min_break1 = timefinish_break1.split(':') 
            start_break1 = datetime(int(year), int(month), int(day), int(start_hr_break1), int(start_min_break1))
            end_break1 = datetime(int(year), int(month), int(day), int(finish_hr_break1), int(finish_min_break1))
            dif_break1 = end_break1 - start_break1 

            dif_hours_break1 = dif_break1.seconds // 3600
            dif_sec_break1 = dif_break1.seconds % 3600
            dif_min_break1 = dif_sec_break1 // 60
            if dif_min_break1 < 10 or dif_min_break1 == 0:
                bt = f'{dif_hours_break1}:0{dif_min_break1}'
            else:
                bt = f'{dif_hours_break1}:{dif_min_break1}'

            # Work time in seconds without break
            diff = end - start - dif_break1 

        #LANCH
        elif timestart_break2 and timefinish_break2:
            start_hr_break2, start_min_break2 = timestart_break2.split(':')  
            finish_hr_break2, finish_min_break2 = timefinish_break2.split(':') 
            start_break2 = datetime(int(year), int(month), int(day), int(start_hr_break2), int(start_min_break2))
            end_break2 = datetime(int(year), int(month), int(day), int(finish_hr_break2), int(finish_min_break2))
            dif_break2 = end_break2 - start_break2

            dif_hours_break2 = dif_break2.seconds // 3600
            dif_sec_break2 = dif_break2.seconds % 3600
            dif_min_break2 = dif_sec_break2 // 60
            if dif_min_break2 < 10 or dif_min_break2 == 0:
                bt = f'{dif_hours_break2}:0{dif_min_break2}'
            else:
                bt = f'{dif_hours_break2}:{dif_min_break2}'

            # Work time in seconds without break
            diff = end - start - dif_break2

        elif timestart_break1 and timefinish_break1 and timestart_break2 and timefinish_break2:
            start_hr_break1, start_min_break1 = timestart_break1.split(':')  
            finish_hr_break1, finish_min_break1 = timefinish_break1.split(':') 
            start_break1 = datetime(int(year), int(month), int(day), int(start_hr_break1), int(start_min_break1))
            end_break1 = datetime(int(year), int(month), int(day), int(finish_hr_break1), int(finish_min_break1))
            dif_break1 = end_break1 - start_break1 
            start_hr_break2, start_min_break2 = timestart_break2.split(':')  
            finish_hr_break2, finish_min_break2 = timefinish_break2.split(':') 
            start_break2 = datetime(int(year), int(month), int(day), int(start_hr_break2), int(start_min_break2))
            end_break2 = datetime(int(year), int(month), int(day), int(finish_hr_break2), int(finish_min_break2))
            dif_break2 = end_break2 - start_break2

            dif_hours_break2 = dif_break1.seconds // 3600
            dif_sec_break1 = dif_break1.seconds % 3600
            dif_min_break1 = dif_sec_break1 // 60
            if dif_min_break1 < 10 or dif_min_break1 == 0:
                bt = f'{dif_hours_break1}:0{dif_min_break1}'
            else:
                bt = f'{dif_hours_break1}:{dif_min_break1}'

            # Work time in seconds without break
            diff = end - start - dif_break1 - dif_break2

        else:
            # Work time in seconds without break
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

        # work_object = request.POST.get('work_object')
        # work_type = request.POST.get('work_type')
        # coffee_food = request.POST.get('coffee_food')
        # fuel = request.POST.get('fuel')
        # prepayment = request.POST.get('prepayment')
        # phone_costs = request.POST.get('phone_costs')
        try:
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
            # if material_costs:
            work.material_costs = float(material_costs)
            work.coffee_food = coffee_food
            work.prepayment = prepayment
            work.fuel = fuel
            work.phone_costs = phone_costs
            work.payment = (user.payment / 3600) * diff.seconds      
            work.timestart_break1 = timestart_break1
            work.timefinish_break1 = timefinish_break1
            work.timestart_break2 = timestart_break2
            work.timefinish_break2 = timefinish_break2 
            work.save()
        except Exception as e:
            error = f'Wystąpił błąd: {e}'
            return render(request, 'error.html', context=error)
        return redirect('raports')
    else:
        work_objects = WorkObject.objects.filter(user__id=user.id)
        work_type = WorkType.objects.all()

    context = {
        'work': work,
        'work_objects': work_objects,
        'work_type': work_type,
        }
    return render(request, 'update_user_work.html', context)


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


#**********************************************************************************************************************#
#****************************************************** USER RAPORT ***************************************************#
#**********************************************************************************************************************#


def getUserRaport(request, user_pk):
    user = get_object_or_404(CustomUser, id=user_pk)
    work_objects = WorkObject.objects.filter(user__id=user_pk)
    if request.user.is_superuser:
        try:
            works = Work.objects.filter(user=user).order_by('-date')
        except Exception as e:
            error = f'Nie można wyświetlić raport z powodu błędu: {e}'
            return render(request, 'error.html', context=error)
    else:
        try:
            works = Work.objects.filter(user=request.user).order_by('-date')
        except Exception as e:
            error = f'Nie można wyświetlić raport z powodu błędu: {e}'
            return render(request, 'error.html', context=error)
        
    ######################
    ### Totals for all ###

    total_fields = {
        'total_material_costs': 'material_costs',
        'total_coffee_food': 'coffee_food',
        'total_fuel': 'fuel',
        'total_prepayment': 'prepayment',
        'total_phone_costs': 'phone_costs',
        'total_payment': 'payment',
        'total_sum_time_sec': 'sum_time_sec',
        'total_sum_over_time_sec': 'sum_over_time_sec'
    }

    totals = {}
    for field_name, field in total_fields.items():
        total = Work.objects.filter(
            user__id=user_pk
            ).aggregate(
            total=Sum(field)
            )['total']
        totals[field_name] = total

    ### End Totals for all ###
    ##########################

    if request.method == 'POST':
        if 'marked' in request.POST:
            marked = request.POST.getlist('marked')
            request.session['marked'] = marked
            if marked is not None:
                return redirect ('deleteListUserWorkQuestion')
            
        ### Sorted by date 
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
            try:
                # works = Work.objects.filter(
                #     date__range=(start, end),
                #     user__id=user_pk,
                # ).order_by('date')
                works = Work.objects.prefetch_related('user').filter(
                    date__range=(start, end),
                ).order_by('-date')
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context=error)

            # Totals
            totals = {}
            for field_name, field in total_fields.items():
                total = works.aggregate(
                    total=Sum(field)
                    )['total']
                totals[field_name] = total

        
        #####################################################################################
        ###################################  WORK OBJECT  ###################################
        #####################################################################################

        if work_object: 
            wo = get_object_or_404(WorkObject, id=work_object)
            try:
                works = Work.objects.filter(
                    work_object=wo.name,
                    user__id=user_pk,
                    ).order_by('date')
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context=error)
            
            # Totals
            totals = {}
            for field_name, field in total_fields.items():
                total = works.aggregate(
                    total=Sum(field)
                    )['total']
                totals[field_name] = total
        
        #####################################################################################
        ##########################  SORTED FROM & WORK OBJECT  ##############################
        #####################################################################################

        if sorted_from and work_object:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))
            wo = WorkObject.objects.get(id=work_object)
            try:
                works = Work.objects.filter(
                        date__range=(start, end),
                        work_object=wo.name,
                        user__id=user_pk,
                    ).order_by('date')
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context=error)
            
            # Totals
            totals = {}
            for field_name, field in total_fields.items():
                total = works.aggregate(
                    total=Sum(field)
                    )['total']
                totals[field_name] = total

    if totals['total_sum_time_sec']: 
        ### total_sum_time_sec => hours:minutes ###
        total_hours = totals['total_sum_time_sec'] // 3600
        total_sec = totals['total_sum_time_sec'] % 3600
        total_min = total_sec // 60
        total_work_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_time = '0:00'
    if totals['total_sum_over_time_sec']:
        ### total_sum_over_time_sec => hours:minutes ###
        total_hours = totals['total_sum_over_time_sec'] // 3600
        total_sec = totals['total_sum_over_time_sec'] % 3600
        total_min = total_sec // 60
        if total_min < 10 or total_min == 0.0:
            total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
        else:
            total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_over_time = '0:00'

    paginator = Paginator(works, 35)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user': user,
        'works': works,
        'work_objects': work_objects,
        'total_material_costs': totals['total_material_costs'],
        'total_coffee_food': totals['total_coffee_food'],
        'total_fuel': totals['total_fuel'],
        'total_prepayment': totals['total_prepayment'],
        'total_phone_costs': totals['total_phone_costs'],
        'total_payment': totals['total_payment'],
        'total_work_time': total_work_time,
        'total_work_over_time': total_work_over_time,
        'page_obj': page_obj,
    }
    return render(request, 'user_raport.html', context)


#**********************************************************************************************************************#
#*************************************************** WORK OBJECT RAPORT ***********************************************#
#**********************************************************************************************************************#


def workObjectRaport(request, user_pk, object_pk):

    total_fields = {
                'total_coffee_food': 'coffee_food',
                'total_fuel': 'fuel',
                'total_prepayment': 'prepayment',
                'total_phone_costs': 'phone_costs',
                'total_payment': 'payment',
                'total_sum_time_sec': 'sum_time_sec',
                'total_sum_over_time_sec': 'sum_over_time_sec'
            }

    ### Sorted by workobject ###
    work_object = get_object_or_404(WorkObject, id=object_pk)

    ### Sorted by date continue.. ###
    try:
        work_by_date = Work.objects.filter(
            user__id=user_pk,
            work_object=work_object.name,
        ).order_by('date')
    except Exception as e:
        error = f'Nie można wyświetlić raport z powodu błędu: {e}'
        return render(request, 'error.html', context=error)

    # Totals
    totals = {}
    for field_name, field in total_fields.items():
        total = work_by_date.aggregate(total=Sum(field))['total']
        if total:
            totals[field_name] = round(total, 2)
        else:
            totals[field_name] = 0.00
    
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
            work_object = get_object_or_404(WorkObject, id=object_pk)

            ### Sorted by date continue.. ###
            try:
                work_by_date = Work.objects.filter(
                    user__id=user_pk,
                    date__range=(start, end),
                    work_object=work_object.name,
                ).order_by('date')
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context=error)

            # Totals
            totals = {}
            for field_name, field in total_fields.items():
                total = work_by_date.aggregate(total=Sum(field))['total']
                totals[field_name] = total

    ## Open page without filtering
    # if totals['total_coffee_food'] is None and \
    #    totals['total_prepayment'] is None and \
    #    totals['total_fuel'] is None and \
    #    totals['total_phone_costs'] is None and \
    #    totals['total_payment'] is None:
    #     totals['total_coffee_food'] = 0.00
    #     totals['total_prepayment'] = 0.00
    #     totals['total_fuel'] = 0.00
    #     totals['total_phone_costs'] = 0.00
    #     totals['total_payment'] = 0.00
    
    total_lists = [
        totals['total_payment'],
        totals['total_phone_costs'],
        totals['total_fuel'],
        totals['total_coffee_food']
    ]

    if any(element is not None for element in total_lists):
        total = sum(total_lists)
    else:
        total = '0:00'
        totals['total_payment'] = '0:00'
        totals['total_prepayment'] = '0:00'
        totals['total_phone_costs'] = '0:01'
        totals['total_fuel'] = '0:00'
        totals['total_coffee_food'] = '0:00'

    ### End Totals for choice ###
    #############################
    
    if totals['total_sum_time_sec']: 
        ### total_sum_time_sec => hours:minutes ###
        total_hours = totals['total_sum_time_sec'] // 3600
        total_sec = totals['total_sum_time_sec'] % 3600
        total_min = total_sec // 60
        total_work_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_time = '0:00'
    if totals['total_sum_over_time_sec']:
        ### total_sum_over_time_sec => hours:minutes ###
        total_hours = totals['total_sum_over_time_sec'] // 3600
        total_sec = totals['total_sum_over_time_sec'] % 3600
        total_min = total_sec // 60
        if total_min < 10 or total_min == 0.0:
            total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
        else:
            total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
    else:
        total_work_over_time = '0:00'

    context = {
        'work_by_date': work_by_date,
        'work_object': work_object,
        'total_coffee_food': totals['total_coffee_food'],
        'total_fuel': totals['total_fuel'],
        'total_prepayment': totals['total_prepayment'],
        'total_phone_costs': totals['total_phone_costs'],
        'total_payment': totals['total_payment'],
        'total_work_time': total_work_time,
        'total_work_over_time': total_work_over_time,
    }
    return render(request, 'workobject_raport.html', context)


#**********************************************************************************************************************#
#****************************************************** ALL RAPORTS ***************************************************#
#**********************************************************************************************************************#


def raports(request):

    total_fields = {
                'total_material_costs': 'material_costs',
                'total_coffee_food': 'coffee_food',
                'total_fuel': 'fuel',
                'total_prepayment': 'prepayment',
                'total_phone_costs': 'phone_costs',
                'total_payment': 'payment',
                'total_sum_time_sec': 'sum_time_sec',
                'total_sum_over_time_sec': 'sum_over_time_sec'
            }
    
    if request.user.is_superuser:
        try:
            works_result = raports_all_superuser.delay() 
            works = works_result.get()
            # print('WORKS!!!!!!!', works)
            # works = Work.objects.prefetch_related(
            #     Prefetch('user')
            #     ).order_by('-date')
            # # Convert Decimal values to float using dictionary comprehension
            # works_dict = [work.__dict__ for work in works]
            # works = [
            #     {key: float(value) if isinstance(value, Decimal) 
            #      else value for key, value in work.items() 
            #      if key != '_state' and key != '_prefetched_objects_cache'} 
            #      for work in works_dict
            #     ]
            work_objects = WorkObject.objects.all().only('name')

        except Exception as e:
            error = f'Nie można wyświetlić raport z powodu błędu: {e}'
            return render(request, 'error.html', context={'error': error})
    else:
        try:
            works_result = raports_all.delay(request.user.id)
            works = works_result.get()
            # works = Work.objects.prefetch_related(
            #     Prefetch('user')
            #     ).filter(
            #     user__id=request.user.id
            #     ).order_by('-date')
            # # Convert Decimal values to float using dictionary comprehension
            # works_dict = [work.__dict__ for work in works]
            # works = [
            #     {key: float(value) if isinstance(value, Decimal) 
            #      else value for key, value in work.items() 
            #      if key != '_state' and key != '_prefetched_objects_cache'} 
            #      for work in works_dict
            #     ]
            work_objects = WorkObject.objects.filter(user=request.user).only('name')
        except Exception as e:
            error = f'Nie można wyświetlić raport z powodu błędu: {e}'
            return render(request, 'error.html', context={'error': error})
        
    users = CustomUser.objects.all().values('id', 'username')
        
    # Totals without filters
    totals = {}
    if works:
        for field_name, field in total_fields.items():
            # total = works.aggregate(total=Sum(F(field)))['total']
            total = sum(work[field] for work in works)
            totals[field_name] = round(total, 2)
    else:
        for field_name, field in total_fields.items():
            totals[field_name] = 0.00

    # Filters
    if request.method == 'POST':

        if 'marked' in request.POST:
            marked = request.POST.getlist('marked')
            request.session['marked'] = marked
            if marked is not None:
                return redirect ('deleteListUserWorkQuestion')

        sorted_from = request.POST.get('sorted_from')
        user = request.POST.get('user')
        work_object = request.POST.get('work_object')

        #####################################################################################
        #######################################  ALL  #######################################
        #####################################################################################

        # if sorted_from and user and work_object == '':
        #     try:
        #         works = Work.objects.all().order_by('-date')
        #         # Convert Decimal values to float using dictionary comprehension
        #         works_dict = [work.__dict__ for work in works]
        #         works = [
        #             {key: float(value) if isinstance(value, Decimal) 
        #              else value for key, value in work.items() 
        #              if key != '_state'} 
        #              for work in works_dict
        #             ]
        #     except Exception as e:
        #         error = f'Nie można wyświetlić raport z powodu błędu: {e}'
        #         return render(request, 'error.html', context=error)
        #     ### Making the excel file of raports ###
        #     if user == '' and work_object == '' and sorted_from == '':
        #         filterRaport = request.POST.get('filterRaport')
        #         if filterRaport == 'download':
        #             request.session['works'] = list(works)
        #             return redirect('raportsToExcel')
            
        #     # Totals 
        #     totals = {}
        #     for field_name, field in total_fields.items():
        #         total = works.aggregate(total=Sum(field))['total']
        #         totals[field_name] = round(total, 2)

        #####################################################################################
        ###################################  SORTED FROM  ###################################
        #####################################################################################

        if sorted_from:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))

            # Call task from task.py
            try:
                works_task = raports_sorted_from.delay(start, end)
                works = works_task.get()
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})

            ### Making the excel file of raports ###
            if user == '' and work_object == '':
                filterRaport = request.POST.get('filterRaport')
                if filterRaport == 'download':
                    request.session['works'] = list(works)
                    return redirect('raportsToExcel')
            
            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                # total = works.aggregate(total=Sum(field))['total']
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)


        #####################################################################################
        #######################################  USER  ######################################
        #####################################################################################

        if user:
            # Call task from task.py
            try:
                works_result = raports_user.delay(user)
                works = works_result.get()
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})
            if sorted_from == '' and work_object == '':
                ### Making the excel file of raports ###
                try:
                    filterRaport = request.POST.get('filterRaport')
                except Exception as e:
                    error = f'Wystąpił błąd: {e}'
                    return render(request, 'error.html', context={'error': error})
                if filterRaport == 'download':
                    try:
                        request.session['works'] = list(works)
                    except Exception as e:
                        error = f'Nie można pobrać raportu z powodu błędu: {e}'
                        return render(request, 'error.html', context={'error': error})
                    return redirect('raportsToExcel')
            
            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                # total = works.aggregate(total=Sum(field))['total']
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)


        #####################################################################################
        ###################################  WORK OBJECT  ###################################
        #####################################################################################

        if work_object: 
            # Call task from task.py
            try:
                works_result = raports_work_object.delay(work_object)
                works = works_result.get()
                # wo = get_object_or_404(WorkObject, id=work_object)
                # works = Work.objects.filter(work_object=wo.name).order_by('-date')
                # # Convert Decimal values to float using dictionary comprehension
                # works_dict = [work.__dict__ for work in works]
                # works = [
                #     {key: float(value) if isinstance(value, Decimal) 
                #      else value for key, value in work.items() 
                #      if key != '_state'} 
                #      for work in works_dict
                #     ]
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})
            if sorted_from == '' and user == '':
                ### Making the excel file of raports ###
                filterRaport = request.POST.get('filterRaport')
                if filterRaport == 'download':
                    request.session['works'] = list(works)
                    return redirect('raportsToExcel')
            
            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                # total = works.aggregate(total=Sum(field))['total']
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)


        #####################################################################################
        ##########################  SORTED FROM & WORK OBJECT  ##############################
        #####################################################################################

        if sorted_from and work_object:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))

            # Call task from task.py
            try:
                works_result = raports_sorted_from_work_object.delay(start, end, work_object)
                works = works_result.get()
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})
            if user == '':
                ### Making the excel file of raports ###
                filterRaport = request.POST.get('filterRaport')
                if filterRaport == 'download':
                    request.session['works'] = list(works)
                    return redirect('raportsToExcel')
            

            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)


        #####################################################################################
        #################################  SORTED FROM & USER  ##############################
        #####################################################################################

        if sorted_from and user:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day))
            end = datetime(int(year_), int(month_), int(day_))

            # Call task from task.py
            try:
                works_result = raports_sorted_from_user.delay(start, end, user)
                works = works_result.get()
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})
            if work_object == '':
                ### Making the excel file of raports ###
                filterRaport = request.POST.get('filterRaport')
                if filterRaport == 'download':
                    request.session['works'] = list(works)
                    return redirect('raportsToExcel')

            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)


        #####################################################################################
        #################################  WORK OBJECT & USER  ##############################
        #####################################################################################

        if work_object and user:

            # Call task from task.py
            try:
                works_result = raports_work_object_user.delay(work_object, user)
                works = works_result.get()
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})
            if sorted_from == '':
                ### Making the excel file of raports ###
                filterRaport = request.POST.get('filterRaport')
                if filterRaport == 'download':
                    request.session['works'] = list(works)
                    return redirect('raportsToExcel')

            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)


        #####################################################################################
        ##########################  SORTED FROM & WORK OBJECT & USER  #######################
        #####################################################################################  

        if sorted_from and user and work_object:

            # Call task from task.py
            try:
                works_result = raports_sorted_from_work_object_user.delay(start, end, work_object, user)
                works = works_result.get()
            except Exception as e:
                error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                return render(request, 'error.html', context={'error': error})
            ### Making the excel file of raports ###
            filterRaport = request.POST.get('filterRaport')
            if filterRaport == 'download':
                request.session['works'] = list(works)
                return redirect('raportsToExcel')
            # Totals 
            totals = {}
            for field_name, field in total_fields.items():
                total = sum(work[field] for work in works)
                totals[field_name] = round(total, 2)
    
    if totals:
        if totals['total_sum_time_sec']: 
            ### total_sum_time_sec => hours:minutes ###
            total_hours = totals['total_sum_time_sec'] // 3600
            total_sec = totals['total_sum_time_sec'] % 3600
            total_min = total_sec // 60
            total_work_time = f'{int(total_hours)}:{int(total_min)}'
        else:
            total_work_time = '0:00'
        if totals['total_sum_over_time_sec']:
            ### total_sum_over_time_sec => hours:minutes ###
            total_hours = totals['total_sum_over_time_sec'] // 3600
            total_sec = totals['total_sum_over_time_sec'] % 3600
            total_min = total_sec // 60
            if total_min < 10 or total_min == 0.0:
                total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
            else:
                total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
        else:
            total_work_over_time = '0:00'

    paginator = Paginator(works, 35)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    ## List of users, even if the someone has been deleted can be find in raports
    works = Work.objects.values_list('username')
    users_list = set()
    users_list = {wo[0] for wo in works}

    total_lists = [
        totals['total_payment'],
        totals['total_phone_costs'],
        totals['total_fuel'],
        totals['total_material_costs'],
        totals['total_coffee_food'],
        totals['total_material_costs'],
    ]

    if any(element is not None for element in total_lists):
        total = sum(total_lists)
    else:
        total = '0:00'
        totals['total_payment'] = '0:00'
        totals['total_prepayment'] = '0:00'
        totals['total_phone_costs'] = '0:00'
        totals['total_fuel'] = '0:00'
        totals['total_coffee_food'] = '0:00'
        totals['total_material_costs'] = '0.00'

    context = {
        'works': works,
        'users': users, 
        'work_objects': work_objects,
        'total_material_costs': totals['total_material_costs'],
        'total_coffee_food': totals['total_coffee_food'],
        'total_fuel': totals['total_fuel'],
        'total_prepayment': totals['total_prepayment'],
        'total_phone_costs': totals['total_phone_costs'],
        'total_payment': totals['total_payment'],
        'total_work_time': total_work_time,
        'total_work_over_time': total_work_over_time,
        'page_obj': page_obj,
        'users_list': users_list,
        'total': total,
    }
    return render(request, 'raports.html', context)


#**********************************************************************************************************************#
#****************************************************** VACATIONS *****************************************************#
#**********************************************************************************************************************#

def vacations(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    try:
        users = Vacations.objects.all().values('username')
        username_list = [user['username'] for user in users]
        vacations = Vacations.objects.filter(user__id=user.id).order_by('-id')
    except Exception as e:
                error = f'Nie można wyświetlić urlopów z powodu błędu: {e}'
                return render(request, 'error.html', context=error)
    years_list = [vacation.v_from[:4] for vacation in vacations] 
    paginator = Paginator(vacations, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    request.session['users'] = username_list
    all_years = Vacations.objects.all()
    all_years_list = [year.v_from[:4] for year in all_years]
    request.session['years'] = sorted(list(set(all_years_list)))

    ## Days quantity from the first day of the year
    today = date.today()
    start_of_year = date(today.year, 1, 1)
    days_since_start = (today - start_of_year).days

    ## Days of vacations DE actually to use in current year
    current_month = datetime.now().month
    try:
        days_to_use = user.vacations_days_quantity_de / 12 * current_month
        vacations.actually_days_to_use = round(days_to_use)
    except:
        error = 'Twoje dane nie zostały uzupełnione, zwróć się do Administartora.'
        return render(request, 'error.html', {'error': error})

    today = date.today()
    first_day_of_the_year = date(today.year, 1, 1)

    ## Changes quantity of vacations to default when the new year is started
    if today == first_day_of_the_year:
        user.last_year_vacations_days_quantity_de = user.days_to_use_in_current_year_de
        user.days_to_use_in_current_year_de = user.vacations_days_quantity_de
        user.save()

    ## Making a vacation request
    if request.method == 'POST':
        if 'user' in request.POST:
            user_option = request.POST.get('user')
            try:
                user = CustomUser.objects.get(username=user_option)
            except:
                return render(request, 'error.html', {'error': 'Użytkownik nie istnije'})
            return redirect('vacations', user.id)

        elif 'year' in request.POST:
            year = request.POST.get('year')
            if year is not None:
                try:
                    vacations = Vacations.objects.filter(
                        user__id=request.user.id,
                        v_from__startswith=year,
                        ).order_by('-id')
                except Exception as e:
                    error = f'Nie można wyświetlić raport z powodu błędu: {e}'
                    return render(request, 'error.html', context=error)
        elif 'marked' in request.POST:
            marked = request.POST.getlist('marked')
            if marked is not None:
                request.session['marked'] = marked # Here we need to send this list to the delete_vacations_requests function
                return redirect('delete_vacations_question')

    context = {
        'vacations': vacations,
        'user': user,
        'users': set(username_list),
        'actually_days_to_use': vacations.actually_days_to_use,
        'years_list': set(years_list),
        'days_used_in_current_year': user.vacations_days_quantity_de - user.days_to_use_in_current_year_de,
        'last_year_vacations_used_days_quantity': user.vacations_days_quantity_de - user.last_year_vacations_days_quantity_de,
        'page_obj': page_obj,
    }
    return render(request, 'vacations.html', context)

def delete_vacations_question(request):
    return render(request, 'delete_vacations_question.html')


def delete_vacations(request):
    marked = request.session.get('marked') # Here we get this list from vacations marked form
    pk = request.user.pk
    markeds = Vacations.objects.filter(
                    id__in=marked
                )
    if markeds:
        for marked in markeds:
            marked.delete()
        return redirect('vacations', pk)
    context = {
        'pk': pk
    }
    return render(request, 'delete_vacations_question.html', context)


def vacationsExcelPage(request):
    users = request.session.get('users')
    years = request.session.get('years')

    if request.method == 'POST':
        user = request.POST.get('user')
        year = request.POST.get('year')
        request.session['user'] = user
        request.session['year'] = year
        print('user', user)
        print('year', year)
        return redirect('vacationsToExcel')
    context = {
        'users': users,
        'years': years,
    }
    return render(request, 'vacationsExcelPage.html', context)


####################################################################################
#                                       EXCEL                                      #
####################################################################################

def vacationsToExcel(request):
    user = request.session.get('user')
    year = request.session.get('year') 
    if user == '' and year is not None:
        vacations = Vacations.objects.filter(
            v_from__startswith=year,
        ).order_by('-id')
    elif user == '' and year == '':
        vacations = Vacations.objects.all().order_by('-id')
    elif user is not None and year is not None:
        vacations = Vacations.objects.filter(
            v_from__startswith=year,
            username=user
        ).order_by('-id')

    wb = openpyxl.Workbook()

    # Get the default active sheet
    sheet = wb.active

    # Add the table headers
    headers = [
        'UŻYTKOWNIK', 
        'DATA WNIOSKU', 
        'TYP',
        'OD',
        'DO',
        'ILOŚĆ DNI',
        'AKCEPTACJA',
        ]  # Specify your desired headers
    for col_num, header in enumerate(headers, 1):
        sheet.cell(row=1, column=col_num).value = header

    # Add the table data
    for row_num, vacation in enumerate(vacations, 2):
        sheet.cell(row=row_num, column=1).value = vacation.username
        sheet.cell(row=row_num, column=2).value = vacation.date
        sheet.cell(row=row_num, column=3).value = vacation.type
        sheet.cell(row=row_num, column=4).value = vacation.v_from
        sheet.cell(row=row_num, column=5).value = vacation.v_to
        sheet.cell(row=row_num, column=6).value = vacation.days_planned
        if vacation.accepted == True:
            sheet.cell(row=row_num, column=7).value = 'Tak'
        else:
            sheet.cell(row=row_num, column=7).value = 'Nie'

    # Set the width of columns
    column_widths = [15, 15, 25, 15, 15, 10, 10]  # Specify the desired width for each column
    for col_num, width in enumerate(column_widths, 1):
        column_letter = get_column_letter(col_num)
        sheet.column_dimensions[column_letter].width = width

    # Create a response to serve the Excel file for download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=urlopy.xlsx'
    wb.save(response)

    return response


def raportsToExcel(request):

    total_fields = {
                'total_coffee_food': 'coffee_food',
                'total_fuel': 'fuel',
                'total_prepayment': 'prepayment',
                'total_phone_costs': 'phone_costs',
                'total_payment': 'payment',
                'total_sum_time_sec': 'sum_time_sec',
                'total_sum_over_time_sec': 'sum_over_time_sec'
            }
    works = request.session.get('works')
    ids = [w['id'] for w in works]

    if request.method == 'POST' or works:
        visible_values = request.POST.getlist('visible_values[]')
        raports = Work.objects.filter(id__in=visible_values)
        if works:
            raports = Work.objects.filter(id__in=ids)

        # Totals 
    #     totals = {}
    #     for field_name, field in total_fields.items():
    #         total = raports.aggregate(total=Sum(field))['total']
    #         totals[field_name] = round(total, 2)

    #     if totals['total_sum_time_sec']: 
    #         ### total_sum_time_sec => hours:minutes ###
    #         total_hours = totals['total_sum_time_sec'] // 3600
    #         total_sec = totals['total_sum_time_sec'] % 3600
    #         total_min = total_sec // 60
    #         total_work_time = f'{int(total_hours)}:{int(total_min)}'
    #     else:
    #         total_work_time = '0:00'
    #     if totals['total_sum_over_time_sec']:
    #         ### total_sum_over_time_sec => hours:minutes ###
    #         total_hours = totals['total_sum_over_time_sec'] // 3600
    #         total_sec = totals['total_sum_over_time_sec'] % 3600
    #         total_min = total_sec // 60
    #         if total_min < 10 or total_min == 0.0:
    #             total_work_over_time = f'{int(total_hours)}:0{int(total_min)}'
    #         else:
    #             total_work_over_time = f'{int(total_hours)}:{int(total_min)}'
    #     else:
    #         total_work_over_time = '0:00'


    # total_lists = [
    #     totals['total_payment'],
    #     totals['total_phone_costs'],
    #     totals['total_fuel'],
    #     totals['total_coffee_food']
    # ]

    # if any(element is not None for element in total_lists):
    #     total = sum(total_lists)
    # else:
    #     total = '0:00'
    #     totals['total_payment'] = '0:00'
    #     totals['total_prepayment'] = '0:00'
    #     totals['total_phone_costs'] = '0:00'
    #     totals['total_fuel'] = '0:00'
    #     totals['total_coffee_food'] = '0:00'

        total_coffee_food = float(raports.aggregate(total_coffee_food=Sum('coffee_food'))['total_coffee_food'])
        total_fuel = float(raports.aggregate(total_fuel=Sum('fuel'))['total_fuel'])
        total_prepayment = float(raports.aggregate(total_prepayment=Sum('prepayment'))['total_prepayment'])
        total_phone_costs = float(raports.aggregate(total_phone_costs=Sum('phone_costs'))['total_phone_costs'])
        total_payment = float(raports.aggregate(total_payment=Sum('payment'))['total_payment'])
        total_sum_time_sec = float(raports.aggregate(total_sum_time_sec=Sum('sum_time_sec'))['total_sum_time_sec'])
        total_sum_over_time_sec = float(raports.aggregate(total_sum_over_time_sec=Sum('sum_over_time_sec'))['total_sum_over_time_sec'])

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

        total = total_coffee_food + total_fuel + total_phone_costs + total_payment

        wb = openpyxl.Workbook()

        # Get the default active sheet
        sheet = wb.active

        # Add the table headers
        headers = [
            'Data', 
            'Pracownik', 
            'Objekt',
            'Początek',
            'Koniec',
            'Czas pracy',
            'Nadgodziny',
            'Czynność',
            'Kawa/Posiłki',
            'Zaliczka',
            'Paliwo',
            'Telefon',
            'Opłata',
            ]  # Specify your desired headers
        for col_num, header in enumerate(headers, 1):
            sheet.cell(row=1, column=col_num).value = header

        # Add the table data
        for row_num, raport in enumerate(raports, 3):
            sheet.cell(row=row_num, column=1).value = raport.date
            sheet.cell(row=row_num, column=2).value = raport.username
            sheet.cell(row=row_num, column=3).value = raport.work_object
            sheet.cell(row=row_num, column=4).value = raport.timestart
            sheet.cell(row=row_num, column=5).value = raport.timefinish
            sheet.cell(row=row_num, column=6).value = raport.diff_time
            sheet.cell(row=row_num, column=7).value = raport.over_time
            sheet.cell(row=row_num, column=8).value = raport.work_type
            sheet.cell(row=row_num, column=9).value = raport.coffee_food
            sheet.cell(row=row_num, column=10).value = raport.prepayment
            sheet.cell(row=row_num, column=11).value = raport.fuel
            sheet.cell(row=row_num, column=12).value = raport.phone_costs
            sheet.cell(row=row_num, column=13).value = raport.payment

        for raport in range(0, 16):
            column_values = ['RAZEM:', total, '', '', '', total_work_time, total_work_over_time, '', 
                            total_coffee_food, total_prepayment, total_fuel, 
                            total_phone_costs, total_payment, '']
            # column_values = ['RAZEM:', '', '', '', '', total_work_time, total_work_over_time, '', 
            #                  totals['total_coffee_food'], totals['total_prepayment'], totals['total_fuel'], 
            #                 totals['total_phone_costs'], totals['total_payment'], '', total]

        for column, value in enumerate(column_values, 1):
            sheet.cell(row=len(raports)+4, column=column).value = value

        # Set the width of columns
        column_widths = [15, 15, 40, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]  # Specify the desired width for each column
        for col_num, width in enumerate(column_widths, 1):
            column_letter = get_column_letter(col_num)
            sheet.column_dimensions[column_letter].width = width

        # Specify the file name for the Excel file
        file_name = 'raporty.xlsx'

        # Construct the full file path
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Save the workbook to the file path
        wb.save(file_path)

        # Create a response to serve the Excel file for download
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=raporty.xlsx'
        wb.save(response)

        return response
    

####################################################################################
#                                  END EXCEL                                       #
####################################################################################


def addVacation(request):
    user = request.user
    date = datetime.now().strftime('%Y-%m-%d')
    types = [
        'wypoczynkowy',
        'bezpłatny',
    ]
    if request.method == 'POST':
        v_from = request.POST.get('v_from')
        v_to = request.POST.get('v_to')
        type = request.POST.get('type')
        days_planned = request.POST.get('days_planned')
        
        ## Potential mistakes from user
        if int(days_planned) <= 0:
            messages.warning(request, 'Prawdopodobnie została niepoprawnie podana data końcowa')
            return redirect('vacations', user.id)
        if type == 'wypoczynkowy' or type == 'na żądanie':   
            if request.user.days_to_use_in_current_year_de == 0:
                messages.warning(request, 'Nie masz więcej urlopu')
                return redirect('vacations', user.id)
            elif type == 'wypoczynkowy' and int(days_planned) > request.user.days_to_use_in_current_year_de  :
                messages.warning(request, f'Masz do dyspozycji tylko {request.user.days_to_use_in_current_year_de } dni urlopu wypoczynkowego')
                return redirect('vacations', user.id)
            elif type == 'na żądanie' and int(days_planned) > 4 :
                messages.warning(request, 'Urlop na żądanie nie może wynosić więcej niż 4 dni')
                return redirect('vacations', user.id)
            elif type == 'na żądanie' and int(days_planned) > request.user.vacacions_on_demand :
                messages.warning(request, f'Masz do dyspozycji tylko {request.user.vacacions_on_demand} dni urlopu na żądanie')
                return redirect('vacations', user.id)
            elif type == 'na żądanie' and request.user.vacacions_on_demand == 0:
                messages.warning(request, 'Urlop na żądanie został wykorzystany')
                return redirect('vacations', user.id)
        elif type == 'opiekuńczy':
            if int(days_planned) > request.user.cares_vacations:
                messages.warning(request, 'Pozostało mniej dni niż potrzebujesz')
                return redirect('vacations', user.id)
            elif request.user.cares_vacations == 0:
                    messages.warning(request, 'Urlop opiekuńczy został wykorzystany')
                    return redirect('vacations', user.id)
        elif type == 'z powodu siły wyższej':
            if int(days_planned) > request.user.force_majeure_vacations:
                messages.warning(request, 'Liczba dni urlopu musi być odpowiednia do pozostałej')
                return redirect('vacations', user.id)
            elif request.user.force_majeure_vacations == 0:
                messages.warning(request, 'Urlop opiekuńczy został wykorzystany')
                return redirect('vacations', user.id)
        elif type == 'okolicznościowy':
            if int(days_planned) > request.user.compassionate_vacations:
                messages.warning(request, 'Liczba dni urlopu musi być odpowiednia do pozostałej')
                return redirect('vacations', user.id)
        elif not days_planned or int(days_planned) == 0:
             messages.warning(request, 'Nie podałeś ilości dni urlopu')
             return redirect('vacations', user.id)
        elif int(days_planned) > request.user.days_to_use_in_current_year_de  and type != 'bezpłatny':
            messages.warning(request, 'Pozostałych dni urlopu mniej niż potrzebujesz')
            return redirect('vacations', user.id)

        try:
            vacation = Vacations(
            user=request.user,
            username=user.username,
            date=date,
            v_from=v_from,
            v_to=v_to,
            type=type,
            days_planned=days_planned,
            consideration=True,
            )
            vacation.save()
            req = VacationRequest(
                v_request=vacation
            )
            req.save()

            ## Looking for same vacations days
            vacs = Vacations.objects.filter(
                accepted=True,
            )
            requesteded_start_date = datetime.strptime(vacation.v_from, '%Y-%m-%d')
            requesteded_end_date = datetime.strptime(vacation.v_to, '%Y-%m-%d')
            for v in vacs:
                accepted_start_date = datetime.strptime(v.v_from, '%Y-%m-%d')
                accepted_end_date = datetime.strptime(v.v_to, '%Y-%m-%d')
                x_date = accepted_start_date
                while x_date <= accepted_end_date:
                    if x_date == requesteded_start_date or x_date == requesteded_end_date:
                        messages.warning(request, 'Ten termin już zarezerwowany, wybierz inny')
                        vacation.delete()
                        return redirect('addVacation')
                    else:
                        x_date += timedelta(days=1)

            messages.success(request, 'Złożyłeś wniosek o urlop')
            return redirect('vacations', user.id)
        except Exception as e:
            messages.warning(request, f'Błąd: {e}. Nie powiodło się, odśwież stronę i spróbój ponownie')
            return redirect(reverse('vacations', user.id))
    
    context = {
        'date': date,
        'types': types,
    }
    return render(request, 'add_vacation.html', context)


## Editing request if it nos accepted yet (only)
def editVacation(request, pk):
    user = request.user
    vacation = Vacations.objects.get(id=pk)
    date = datetime.now().strftime('%Y-%m-%d')
    types = [
        'wypoczynkowy',
        'bezpłatny',
    ]
    if request.method == 'POST':
        v_from = request.POST.get('v_from')
        v_to = request.POST.get('v_to')
        type = request.POST.get('type')
        days_planned = request.POST.get('days_planned')
        
        ## Potential mistakes from user
        if int(days_planned) <= 0:
            messages.warning(request, 'Prawdopodobnie została niepoprawnie podana data końcowa')
            return redirect('vacations', user.id)
        if type == 'wypoczynkowy' or type == 'na żądanie':   
            if request.user.days_to_use_in_current_year_de == 0:
                messages.warning(request, 'Nie masz więcej urlopu')
                return redirect('vacations', user.id)
            elif int(days_planned) > request.user.days_to_use_in_current_year_de :
                messages.warning(request, f'Masz do dyspozycji tylko {request.user.days_to_use_in_current_year_de } dni urlopu wypoczynkowego')
                return redirect('vacations', user.id)
            elif type == 'na żądanie' and int(days_planned) > 4 :
                messages.warning(request, 'Urlop na żądanie nie może wynosić więcej niż 4 dni')
                return redirect('vacations', user.id)
            elif type == 'na żądanie' and int(days_planned) > request.user.vacacions_on_demand  :
                messages.warning(request, f'Masz do dyspozycji tylko {request.user.vacacions_on_demand } dni urlopu na żądanie')
                return redirect('vacations', user.id)
            elif type == 'na żądanie' and request.user.vacacions_on_demand  == 0:
                messages.warning(request, 'Urlop na żądanie został wykorzystany')
                return redirect('vacations', user.id)
        elif type == 'opiekuńczy':
            if int(days_planned) > request.user.cares_vacations:
                messages.warning(request, 'Pozostało mniej dni niż potrzebujesz')
                return redirect('vacations', user.id)
            elif request.user.cares_vacations == 0:
                    messages.warning(request, 'Urlop opiekuńczy został wykorzystany')
                    return redirect('vacations', user.id)
        elif type == 'z powodu siły wyższej':
            if int(days_planned) > request.user.force_majeure_vacations:
                messages.warning(request, 'Liczba dni urlopu musi być odpowiednia do pozostałej')
                return redirect('vacations', user.id)
            elif request.user.force_majeure_vacations == 0:
                messages.warning(request, 'Urlop opiekuńczy został wykorzystany')
                return redirect('vacations', user.id)
        elif type == 'okolicznościowy':
            if int(days_planned) > request.user.compassionate_vacations:
                messages.warning(request, 'Pozostało mniej dni niż potrzebujesz')
                return redirect('vacations', user.id)
        elif not days_planned or int(days_planned) == 0:
             messages.warning(request, 'Nie podałeś ilości dni urlopu')
             return redirect('vacations', user.id)
        elif int(days_planned) > request.user.days_to_use_in_current_year_de and type != 'bezpłatny' :
            messages.warning(request, 'Pozostałych dni urlopu mniej niż potrzebujesz')
            return redirect('vacations', user.id)
    
        try:
            vacation = Vacations.objects.get(id=pk)
            vacation.date = date
            vacation.v_from = v_from
            vacation.v_to = v_to
            vacation.type = type
            vacation.days_planned = int(days_planned)
            vacation.consideration = True
            vacation.save() 
            return redirect('vacations', user.id)
        except Exception as e:
            messages.warning(request, f'Błąd: {e}. Nie powiodło się, odśwież stronę i spróbój ponownie')
            return redirect(reverse('vacations', user.id))

    context = {
        'vacation': vacation,
        'date': date,
        'types': types,
    }
    return render(request, 'edit_vacation.html', context)


def deleteVacationPage(request, pk):
    vacation = Vacations.objects.get(id=pk)
    context = {
        'vacation': vacation,
        }
    return render(request, 'deleteVacationPage.html', context)


def deleteVacation(request, pk):
    user = request.user
    Vacations.objects.filter(id=pk).delete()
    return redirect('vacations', user.id)


def deleteVacationRequestQuestion(request):
    if request.method == 'GET':
        response = {'message': 'ok',}    
    return JsonResponse(response) 


def deleteVacationRequest(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        req_ids = data.get('req', [])
    try:
        for req_id in req_ids:
            vacation_request = VacationRequest.objects.get(id=req_id)
            vacation_request.delete()
    except Exception as e:
        return render(request, 'error.html', 
                      context={f'Wystąpił błąd:': {e}})
    response = {
        'message': 'ok'
    }
    return JsonResponse(response) 


def allVacationRequests(request):
    reqs = VacationRequest.objects.all().order_by('-v_request__id')
    users = CustomUser.objects.all().values('username')
    types = [
        'wypoczynkowy',
        'bezpłatny',
    ]
    paginator = Paginator(reqs, 10)  

    page_number = request.GET.get('page')
    reqs = paginator.get_page(page_number)

    ## Filter
    if request.method == 'POST':
        sorted_from = request.POST.get('sorted_from')
        sorted_to = request.POST.get('sorted_to')
        user = request.POST.get('user')
        type = request.POST.get('type')
        status = request.POST.get('status')

        #####################################################################################
        ###################################  SORTED FROM  ###################################
        #####################################################################################

        if sorted_from and user and type and status:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day)).date()
            end = datetime(int(year_), int(month_), int(day_)).date()
            if status == 'Zaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__date__range=(start, end),
                    v_request__user__username=user,
                    v_request__type=type,
                    v_request__accepted=True,
                )
            elif status == 'Niezaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__date__range=(start, end),
                    v_request__user__username=user,
                    v_request__type=type,
                    v_request__accepted=False,
                )
            elif status == 'Rozpatrywane':
                reqs = VacationRequest.objects.filter(
                    v_request__date__range=(start, end),
                    v_request__user__username=user,
                    v_request__type=type,
                    v_request__consideration=True,
                )
            print('sorted_from and user and type and status', reqs)
           
        elif sorted_from and user and type:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day)).date()
            end = datetime(int(year_), int(month_), int(day_)).date()
            reqs = VacationRequest.objects.filter(
                v_request__date__range=(start, end),
                v_request__user__username=user,
                v_request__type=type,
            )
            print('sorted_from and user and type', reqs)

        elif sorted_from and user:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day)).date()
            end = datetime(int(year_), int(month_), int(day_)).date()
            reqs = VacationRequest.objects.filter(
                v_request__date__range=(start, end),
                v_request__user__username=user,
            )
            print('sorted_from and user', reqs)

        elif sorted_from and type:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day)).date()
            end = datetime(int(year_), int(month_), int(day_)).date()
            reqs = VacationRequest.objects.filter(
                v_request__date__range=(start, end),
                v_request__type=type,
            )
            print('sorted_from and type', reqs)

        elif sorted_from and status:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day)).date()
            end = datetime(int(year_), int(month_), int(day_)).date()
            if status == 'Zaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__date__range=(start, end),
                    v_request__accepted=True,
                )
            elif status == 'Niezaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__date__range=(start, end),
                    v_request__accepted=False,
                )
            elif status == 'Rozpatrywane':
                reqs = VacationRequest.objects.filter(
                    v_request__date__range=(start, end),
                    v_request__consideration=True,
                )
            print('sorted_from and status', reqs)

        elif sorted_from:
            year, month, day = sorted_from.split('-')
            sorted_to = request.POST.get('sorted_to')
            year_, month_, day_ = sorted_to.split('-')
            start = datetime(int(year), int(month), int(day)).date()
            end = datetime(int(year_), int(month_), int(day_)).date()
            reqs = VacationRequest.objects.filter(
                v_request__date__range=(start, end),
            )
            print('sorted_from', reqs)
        
        elif user and type and status:
            if status == 'Zaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__user__username=user,
                    v_request__type=type,
                    v_request__accepted=True,
                )
            elif status == 'Niezaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__user__username=user,
                    v_request__type=type,
                    v_request__accepted=False,
                )
            elif status == 'Rozpatrywane':
                reqs = VacationRequest.objects.filter(
                    v_request__user__username=user,
                    v_request__type=type,
                    v_request__consideration=True,
                )
            print('user and type and status', reqs)

        elif user and type:
            reqs = VacationRequest.objects.filter(
                v_request__user__username=user,
                v_request__type=type,
            )
            print('user and type', reqs)

        elif user and status:
            if status == 'Zaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__user__username=user,
                    v_request__accepted=True,
                )
            elif status == 'Niezaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__user__username=user,
                    v_request__accepted=False,
                )
            elif status == 'Rozpatrywane':
                reqs = VacationRequest.objects.filter(
                    v_request__user__username=user,
                    v_request__consideration=True,
                )
            print('user and status', reqs)

        elif type and status:
            if status == 'Zaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__type=type,
                    v_request__accepted=True,
                )
            elif status == 'Niezaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__type=type,
                    v_request__accepted=False,
                )
            elif status == 'Rozpatrywane':
                reqs = VacationRequest.objects.filter(
                    v_request__type=type,
                    v_request__consideration=True,
                )
            print('type and status', reqs)

        elif user:
            reqs = VacationRequest.objects.filter(
                v_request__user__username=user,
            )
            print('user', reqs)

        elif type:
            reqs = VacationRequest.objects.filter(
                v_request__type=type,
            )
            print('type', reqs)

        elif status:
            if status == 'Zaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__accepted=True,
                )
            elif status == 'Niezaakceptowane':
                reqs = VacationRequest.objects.filter(
                    v_request__accepted=False,
                )
            elif status == 'Rozpatrywane':
                reqs = VacationRequest.objects.filter(
                    v_request__consideration=True,
                )
            print('status', status)
            
    context = {
       'reqs': reqs, 
       'users': users,
       'types': types,
    }
    return render(request, 'all_vacation_requests.html', context)


def vacationRequest(request, pk):

    req = VacationRequest.objects.filter(
        v_request__id=pk
        ).select_related(
        'v_request'
        ).only(
        'v_request__username', 
        'v_request__type', 
        'v_request__date', 
        'v_request__v_from', 
        'v_request__v_to', 
        'v_request__days_planned'
        ).first()
  
    print('VACATIONREQUEST', req.v_request.days_planned, req)
    vacation = Vacations.objects.get(id=pk)
    type = vacation.type

    ## Days quantity from the first day of the year
    today = date.today()
    start_of_year = date(today.year, 1, 1)
    days_since_start = (today - start_of_year).days

    ## Days of vacations DE actually to use in current year
    current_month = datetime.now().month
    days_to_use = vacation.user.vacations_days_quantity_de / 12 * current_month ###
    vacation.actually_days_to_use = round(days_to_use)

    if request.method == 'POST':
        if 'accept' in request.POST and type in ['wypoczynkowy', 'na żądanie']:
            vacation.accepted = True
            vacation.consideration = False
            if vacation.user.last_year_vacations_days_quantity_de > 0: ###
                if req.v_request.days_planned >= vacation.user.last_year_vacations_days_quantity_de: ###
                    vacation.days_used_in_last_year = vacation.user.vacations_days_quantity_de - vacation.days_to_use_in_last_year ###
                    vacation.days_used_in_current_year = req.v_request.days_planned - vacation.user.last_year_vacations_days_quantity_de ###
                    vacation.days_to_use_in_last_year = 0
                    vacation.user.days_to_use_in_current_year_de = vacation.user.vacations_days_quantity_de - vacation.days_used_in_current_year ###
                    vacation.user.last_year_vacations_days_quantity_de = 0 ###
                else:
                    vacation.user.last_year_vacations_days_quantity_de -=  req.v_request.days_planned ###
                    vacation.days_to_use_in_last_year = vacation.user.last_year_vacations_days_quantity_de  ## Duplicate for Vacations model ###
                    vacation.days_used_in_last_year = vacation.user.vacations_days_quantity_de - vacation.user.last_year_vacations_days_quantity_de ###
                    vacation.days_to_use_in_current_year = vacation.user.vacations_days_quantity - vacation.days_used_in_current_year ###
            else:
                vacation.user.days_to_use_in_current_year_de = vacation.user.days_to_use_in_current_year_de - req.v_request.days_planned
                vacation.days_used_in_current_year = vacation.user.vacations_days_quantity_de - vacation.user.days_to_use_in_current_year_de
                vacation.days_used_in_last_year = vacation.user.vacations_days_quantity_de - vacation.user.last_year_vacations_days_quantity_de
            if today == start_of_year:
                vacation.user.last_year_vacations_days_quantity_de = vacation.days_to_use_in_current_year
                vacation.user.days_to_use_in_current_year_de = vacation.user.vacations_days_quantity_de
            vacation.save()
            vacation.user.save()
            return redirect('allVacationRequests')
        
        
        elif 'accept' in request.POST and type == 'bezpłatny':
            vacation.accepted = True
            vacation.consideration = False
            vacation.save()
            return redirect('allVacationRequests')

        elif 'reject' in request.POST:
            vacation.accepted = False
            vacation.consideration = False
            vacation.save()
            return redirect('allVacationRequests')
    context = {
        'req': vacation,
        'pk': pk,
    }
    return render(request, 'vacation_request.html', context)
    

####################################################################################
#                                  END EXCEL                                       #
####################################################################################


def upload_document(request):
    users = CustomUser.objects.values_list('username', flat=True).order_by('id')
    users_ids = CustomUser.objects.values_list('id', flat=True).order_by('id')
    documents = Documents.objects.all()
    users_ = CustomUser.objects.values('id', 'username')
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        title = request.POST['title']
        username = request.POST['user']
        user = get_object_or_404(CustomUser, username=username)
        
        document = Documents(
            title=title, 
            document=uploaded_file,
            user=user,
            )
        document.save()

        return redirect('upload_document')

    context = {
        'users': users,
        'users_ids': users_ids,
        'documents': documents,
        'users_': users_,
    }

    return render(request, 'documents.html', context)


def getDocuments(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    try:
        documents = Documents.objects.filter(user=user)
    except Exception as e:
        return render(request, 'error.html', context={'Błąd': e})
    context = {
        'documents': documents,
    }

    return render(request, 'get_documents.html', context)


def deleteDocument(request):
    if request.method == "POST":
        pk = request.POST.get('pk')
        print('pk --------------', pk)
        document = get_object_or_404(Documents, id=int(pk))
        print('document --------------', document)
        document.delete()

        response = {
            'status': 'deleted'
        }

        return JsonResponse(response)