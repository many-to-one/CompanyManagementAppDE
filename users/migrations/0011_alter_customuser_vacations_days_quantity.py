# Generated by Django 4.2.1 on 2023-06-14 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_customuser_vacations_days_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='vacations_days_quantity',
            field=models.IntegerField(null=True, verbose_name='Ilość przysługujących dni urlopu'),
        ),
    ]
