# Generated by Django 4.2.1 on 2023-05-09 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(default='00-00-00', max_length=8)),
                ('timestart', models.CharField(default='00:00', max_length=5)),
                ('timefinish', models.CharField(default='00:00', max_length=5)),
            ],
        ),
    ]
