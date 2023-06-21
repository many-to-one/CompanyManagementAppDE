from django import template
from ..models import Message

register = template.Library()

@register.simple_tag
def messages_quantity(pk):
    messages = Message.objects.filter(
        work_object=pk
    )
    return