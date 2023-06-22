# Generated by Django 4.2.1 on 2023-06-22 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0075_remove_message_recipient_message_recipient'),
    ]

    operations = [
        migrations.CreateModel(
            name='IsRead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, null=True)),
                ('is_read', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='message',
            name='recipient',
        ),
        migrations.DeleteModel(
            name='UnreadMessages',
        ),
        migrations.AddField(
            model_name='isread',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.message'),
        ),
    ]