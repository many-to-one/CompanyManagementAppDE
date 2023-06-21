from django import template
from ..models import VacationRequest

register = template.Library()

@register.simple_tag
def request_quantity():
    reqs = VacationRequest.objects.all().order_by('-v_request__id')
    count = 0
    for r in reqs:
        if r.v_request.consideration is True:
            print('count', count)
            count += 1
    return count
