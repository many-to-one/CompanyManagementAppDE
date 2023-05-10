# Generated by Django 4.2.1 on 2023-05-10 19:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0027_remove_workobject_user_workobject_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workobject',
            name='user',
        ),
        migrations.AddField(
            model_name='workobject',
            name='user',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
