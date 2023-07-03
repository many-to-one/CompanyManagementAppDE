# Generated by Django 4.2.1 on 2023-07-03 06:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0079_alter_message_sender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='isread',
            name='message',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.message'),
        ),
        migrations.AlterField(
            model_name='isread',
            name='work_object',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.workobject'),
        ),
    ]
