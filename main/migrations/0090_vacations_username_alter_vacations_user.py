# Generated by Django 4.2.1 on 2023-07-10 14:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0089_alter_task_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacations',
            name='username',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='vacations',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
    ]