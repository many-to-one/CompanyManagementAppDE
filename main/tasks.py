from decimal import Decimal
from time import sleep
from celery import shared_task
from django.shortcuts import get_object_or_404, render
from .models import IsRead, Message, Work, WorkObject
from django.db.models import Q, Prefetch
from django.template import Template, Context



@shared_task
def raports_all_superuser():
    works = Work.objects.prefetch_related(
        Prefetch('user')
        ).order_by('-date')
    # Convert Decimal values to float using dictionary comprehension
    works_dict = [work.__dict__ for work in works]
    works = [
        {key: float(value) if isinstance(value, Decimal) 
         else value for key, value in work.items() 
         if key != '_state' and key != '_prefetched_objects_cache'} 
         for work in works_dict
        ]
    return works


@shared_task
def raports_all(user_id):
    works = Work.objects.prefetch_related(
        Prefetch('user')
        ).filter(
        user__id=user_id
        ).order_by('-date')
    # Convert Decimal values to float using dictionary comprehension
    works_dict = [work.__dict__ for work in works]
    works = [
        {key: float(value) if isinstance(value, Decimal) 
         else value for key, value in work.items() 
         if key != '_state' and key != '_prefetched_objects_cache'} 
         for work in works_dict
        ]
    return works


@shared_task
def raports_sorted_from(start, end):
    works = Work.objects.prefetch_related('user').filter(
            date__range=(start, end),
        ).order_by('-date')
    # Convert Decimal values to float using dictionary comprehension
    works_dict = [work.__dict__ for work in works]
    works = [
        {key: float(value) if isinstance(value, Decimal) 
         else value for key, value in work.items() 
         if key != '_state' and key != '_prefetched_objects_cache'} 
         for work in works_dict
        ]
    return works


@shared_task
def raports_user(user):
    works = Work.objects.filter(username=user).order_by('-date')
    # Convert Decimal values to float using dictionary comprehension
    works_dict = [work.__dict__ for work in works]
    works = [
        {key: float(value) if isinstance(value, Decimal) 
         else value for key, value in work.items() 
         if key != '_state'} 
         for work in works_dict
        ]
    return works


@shared_task
def raports_work_object(work_object_id):
    wo = get_object_or_404(WorkObject, id=work_object_id)
    works = Work.objects.filter(work_object=wo.name).order_by('-date')
    # Convert Decimal values to float using dictionary comprehension
    works_dict = [work.__dict__ for work in works]
    works = [
        {key: float(value) if isinstance(value, Decimal) 
         else value for key, value in work.items() 
         if key != '_state'} 
         for work in works_dict
        ]
    return works


@shared_task
def raports_sorted_from_work_object(start, end, work_object_id):
    wo = get_object_or_404(WorkObject, id=work_object_id)
    works = Work.objects.filter(
        date__range=(start, end),
        work_object=wo.name,
    ).order_by('-date')
    # Convert Decimal values to float using dictionary comprehension
    works_dict = [work.__dict__ for work in works]
    works = [
        {key: float(value) if isinstance(value, Decimal) 
         else value for key, value in work.items() 
         if key != '_state'} 
         for work in works_dict
        ]
    return works


@shared_task
def raports_sorted_from_user(start, end, user):
    works = Work.objects.filter(
        date__range=(start, end),
        username=user,
    ).order_by('-date')
    # Convert Decimal values to float using dictionary comprehension
    works_dict = [work.__dict__ for work in works]
    works = [
        {key: float(value) if isinstance(value, Decimal) 
         else value for key, value in work.items() 
         if key != '_state'} 
         for work in works_dict
        ]
    return works


@shared_task
def raports_work_object_user(work_object_id, user):
    wo = get_object_or_404(WorkObject, id=work_object_id)
    works = Work.objects.filter(
        work_object=wo.name,
        username=user
        ).order_by('-date')
    # Convert Decimal values to float using dictionary comprehension
    works_dict = [work.__dict__ for work in works]
    works = [
        {key: float(value) if isinstance(value, Decimal) 
         else value for key, value in work.items() 
         if key != '_state'} 
         for work in works_dict
        ]
    return works


@shared_task
def raports_sorted_from_work_object_user(start, end, work_object_id, user):
    wo = get_object_or_404(WorkObject, id=work_object_id)
    works = Work.objects.filter(
        date__range=(start, end),
        work_object=wo.name,
        username=user,
    ).order_by('-date')
    # Convert Decimal values to float using dictionary comprehension
    works_dict = [work.__dict__ for work in works]
    works = [
        {key: float(value) if isinstance(value, Decimal) 
         else value for key, value in work.items() 
         if key != '_state'} 
         for work in works_dict
        ]
    return works


@shared_task
def update_is_read_flag(work_object_id, username):
    work_object = get_object_or_404(WorkObject, id=work_object_id)
    try:
        # All messages in current work object
        read_messages = Message.objects.filter(work_object=work_object)

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
        messages = read_messages.values()
    except WorkObject.DoesNotExist:
        raise ValueError (f"WorkObject with ID {work_object_id} does not exist.")
    
    return list(messages)