# Generated by Django 4.2.1 on 2023-06-29 09:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0077_isread_work_object'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='username',
            field=models.CharField(max_length=125, null=True, verbose_name='Imię użytkownika'),
        ),
        migrations.AlterField(
            model_name='isread',
            name='work_object',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='main.workobject'),
        ),
        migrations.AlterField(
            model_name='message',
            name='work_object',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='objekt', to='main.workobject'),
        ),
        migrations.AlterField(
            model_name='vacations',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
    ]