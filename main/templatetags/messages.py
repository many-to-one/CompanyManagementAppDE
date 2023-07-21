from django import template
from ..models import IsRead
from django.db.models import Count

register = template.Library()

@register.simple_tag
def messages_quantity(username, work_object):
    quantity = IsRead.objects.filter(
        username=username,
        work_object=work_object,
        is_read=False,
    )#.exclude(username=username)
    return quantity.count()


@register.simple_tag
def all_messages_quantity(username):
    quantity = IsRead.objects.filter(
        username=username,
        is_read=False,
    )#.exclude(username=username)
    return quantity.count()