# Generated by Django 4.2.1 on 2023-06-15 07:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0065_remove_vacations_days_to_use_in_current_year'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vacations',
            name='days_to_use_in_last_year',
        ),
    ]
