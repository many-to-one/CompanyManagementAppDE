# Generated by Django 4.2.1 on 2023-06-13 13:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0055_vacations_accepted_vacations_consideration'),
    ]

    operations = [
        migrations.CreateModel(
            name='VacationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.vacations')),
            ],
        ),
    ]
