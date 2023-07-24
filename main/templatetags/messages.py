from django import template
from ..models import IsRead, Message

register = template.Library()

@register.simple_tag
def messages_quantity(user, work_object):
    quantity = IsRead.objects.filter(
        username=user.username,
        work_object=work_object,
        is_read=False,
    )

    # According to the logic in test.py: update_is_read_flag()
    # sending's message for sender also marks unread, here we
    # need to find this(thouse) message(s)
    sender_message = IsRead.objects.filter(
        work_object=work_object,
        is_read=False,
        username=user.username,
        message__sender=user,
    )
    # And gere we need to set count for unread messages
    # for sender 0, because his message is also marked 
    # unread
    if sender_message:
        return 0
    
    return quantity.count()


@register.simple_tag
def all_messages_quantity(user):
    quantity = IsRead.objects.filter(
        username=user.username,
        is_read=False,
    )

    # According to the logic in test.py: update_is_read_flag()
    # sending's message for sender also marks unread, here we
    # need to find this(thouse) message(s)
    sender_message = IsRead.objects.filter(
        is_read=False,
        username=user.username,
        message__sender=user,
    )
    # And gere we need to set count for unread messages
    # for sender 0, because his message is also marked 
    # unread
    if sender_message:
        return 0
    return quantity.count()