# Generated by Django 4.2.1 on 2023-07-11 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_customuser_ip_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='ip_address',
            field=models.JSONField(null=True),
        ),
    ]
