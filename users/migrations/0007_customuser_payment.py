# Generated by Django 4.2.1 on 2023-05-15 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_customuser_fp_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='payment',
            field=models.FloatField(default=0, null=True, verbose_name='Stawka za godzinę'),
        ),
    ]
