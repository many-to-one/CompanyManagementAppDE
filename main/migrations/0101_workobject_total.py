# Generated by Django 4.2.1 on 2023-08-15 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0100_subcontractor'),
    ]

    operations = [
        migrations.AddField(
            model_name='workobject',
            name='total',
            field=models.FloatField(default=0, verbose_name='Koszty projektu'),
        ),
    ]