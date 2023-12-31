# Generated by Django 4.2.1 on 2023-06-21 19:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0073_remove_message_recipient_message_recipient'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnreadMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unread_messages', models.IntegerField(default=0)),
                ('user', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('work_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.workobject')),
            ],
        ),
    ]
