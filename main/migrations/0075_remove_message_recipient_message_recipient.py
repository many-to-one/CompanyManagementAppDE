# Generated by Django 4.2.1 on 2023-06-22 09:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0074_unreadmessages'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='recipient',
        ),
        migrations.AddField(
            model_name='message',
            name='recipient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='odbiorca', to=settings.AUTH_USER_MODEL),
        ),
    ]
