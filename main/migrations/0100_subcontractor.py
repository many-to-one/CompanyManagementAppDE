# Generated by Django 4.2.1 on 2023-08-15 07:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0099_workobject_deadline_workobject_finished'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subcontractor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, null=True, verbose_name='Pomocnik/Podwykonawca')),
                ('time', models.FloatField(default=0, verbose_name='Czas pracy')),
                ('price', models.FloatField(default=0, verbose_name='Kosz pracy za godzinę')),
                ('sum', models.FloatField(default=0, verbose_name='Kwota')),
                ('work_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcontractor', to='main.workobject')),
            ],
        ),
    ]
