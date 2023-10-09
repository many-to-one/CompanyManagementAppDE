from django.template import Context, Template
from django.db.models import Q
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from ..tasks import *
from ..models import (
    MessageCount,
    MessageCountUser,
    WorkObject, 
    Message, 
    IsRead, 
    )
from django.http import JsonResponse
from django.conf import settings


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