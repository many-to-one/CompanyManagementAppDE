# Generated by Django 4.2.1 on 2023-07-05 09:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0083_alter_vacations_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, null=True)),
                ('content', models.CharField(max_length=250, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wyconawca', to=settings.AUTH_USER_MODEL)),
                ('work_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='object', to='main.workobject')),
            ],
        ),
    ]