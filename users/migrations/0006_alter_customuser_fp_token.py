# Generated by Django 4.2.1 on 2023-05-11 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_remove_customuser_work_objects_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='fp_token',
            field=models.CharField(max_length=192, null=True, unique=True),
        ),
    ]
