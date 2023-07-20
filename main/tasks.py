from decimal import Decimal
from time import sleep
from celery import shared_task
from django.shortcuts import get_object_or_404, render
from .models import IsRead, Message, Work, WorkObject
from django.db.models import Q, Prefetch


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
        read_messages = Message.objects.filter(work_object=work_object)
        read_filter = Q(message__in=read_messages) & Q(username=username)
        read_for_others = IsRead.objects.filter(
                work_object=work_object,
                is_read=False,
            ).exclude(username=username)
        if read_for_others.count() > 0:
            IsRead.objects.filter(read_filter).exclude(message__sender__username=username).update(is_read=True)
        else:
            IsRead.objects.filter(read_filter).update(is_read=True)
        messages = read_messages.values()
    except WorkObject.DoesNotExist:
        raise ValueError (f"WorkObject with ID {work_object_id} does not exist.")
    
    return list(messages)