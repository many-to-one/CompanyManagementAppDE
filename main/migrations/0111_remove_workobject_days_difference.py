# Generated by Django 4.2.4 on 2023-10-09 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0110_workobject_days_difference'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workobject',
            name='days_difference',
        ),
    ]