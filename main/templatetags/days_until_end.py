from datetime import datetime
from django import template

from main.utils import months_pl_shorts

register = template.Library()

@register.simple_tag
def days_until_end(wo_timefinish):

     # Define a dictionary to map month abbreviations to month numbers
    month_dict = {
        'Sty': '01',
        'Lut': '02',
        'Mar': '03',
        'Kwi': '04',
        'Maj': '05',
        'Cze': '06',
        'Lip': '07',
        'Sie': '08',
        'Wrz': '09',
        'Paź': '10',
        'Lis': '11',
        'Gru': '12'
    }

    # Split the input date string into components
    day, month_abbrev, year = wo_timefinish.split()

    # Convert the month abbreviation to a month number
    month_number = month_dict.get(month_abbrev)

    # Create a new date string in the 'dd.mm.yyyy' format
    new_date_string = f'{day}.{month_number}.{year}'

    current_date = datetime.now().date()
    parsed_finish = datetime.strptime(new_date_string, '%d.%m.%Y').date()

    # Calculate the difference
    date_difference = parsed_finish - current_date

    # Access the days, seconds, and other attributes of the timedelta
    difference = date_difference.days

    if difference >= 0:
        return difference
    else:
        return 0
