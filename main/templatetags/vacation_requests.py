from django import template
from ..models import VacationRequest
from django.db.models import Count

register = template.Library()

@register.simple_tag
def request_quantity():
    reqs = VacationRequest.objects.filter(
        v_request__consideration=True
    ).order_by(
        '-v_request__id'
    ).select_related('v_request')
    return reqs.count()
