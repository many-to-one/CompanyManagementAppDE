from django import template
from ..models import Message, IsRead

register = template.Library()

@register.simple_tag
def messages_quantity(username, work_object):
    count = 0
    quantity = IsRead.objects.filter(
        username=username,
        work_object=work_object,
        is_read=False,
    )
    print('quantity', quantity)
    for q in quantity:
        count += 1
    return count


@register.simple_tag
def all_messages_quantity(username):
    count = 0
    quantity = IsRead.objects.filter(
        username=username,
        is_read=False,
    )
    print('quantity', quantity)
    for q in quantity:
        count += 1
    return count