# Generated by Django 4.2.1 on 2023-05-16 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_customuser_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='payment',
            field=models.FloatField(default=0, verbose_name='Stawka za godzinę'),
        ),
    ]
