# Generated by Django 4.2.1 on 2023-07-11 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_customuser_token_expiration'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlacklistToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True, verbose_name='Data')),
                ('token', models.CharField(max_length=192, unique=True)),
                ('blacklisted_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
