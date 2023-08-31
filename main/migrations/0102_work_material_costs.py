# Generated by Django 4.2.1 on 2023-08-15 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0101_workobject_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='material_costs',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Koszty materiałów'),
        ),
    ]