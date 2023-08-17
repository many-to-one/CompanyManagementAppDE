from datetime import datetime
from django import template

from main.utils import months_pl_shorts

register = template.Library()

@register.simple_tag
def days_until_end(wo_timefinish):
    current_date = datetime.now().date()
    formatted_date = months_pl_shorts(current_date.strftime('%d %b %Y'))
    count = int(wo_timefinish[:2]) - int(formatted_date[:2])
    if count >= 0:
        return count
    else:
        return 0
