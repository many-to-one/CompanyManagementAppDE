# Generated by Django 4.2.1 on 2023-05-05 12:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='adress_de',
            field=models.CharField(max_length=255, null=True, verbose_name='Adres w Niemczech'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='adress_pl',
            field=models.CharField(max_length=255, null=True, verbose_name='Adres w Polsce'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='bank',
            field=models.CharField(max_length=255, null=True, verbose_name='Nazwa banku'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='bank_account',
            field=models.CharField(max_length=255, null=True, verbose_name='Konto i właściciel'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='bic_swift',
            field=models.CharField(max_length=255, null=True, verbose_name='BIC/SWIFT'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='birthday',
            field=models.CharField(max_length=55, null=True, verbose_name='Data urodzenia'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='birthplace',
            field=models.CharField(max_length=255, null=True, verbose_name='Miejsce urodzenia'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='growth',
            field=models.CharField(max_length=255, null=True, verbose_name='Wzrost'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='health_insurance_de',
            field=models.CharField(max_length=255, null=True, verbose_name='Ubezpieczenie w Niemczech'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='health_insurance_de_number',
            field=models.CharField(max_length=255, null=True, verbose_name='KK VersNr'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='insurance_number',
            field=models.CharField(max_length=255, null=True, verbose_name='Numer ubezpieczenia'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='internal_tax_number',
            field=models.CharField(max_length=255, null=True, verbose_name='Wewnętrzny numer podatkowy'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='nfz_adress',
            field=models.CharField(max_length=255, null=True, verbose_name='NFZ - adres'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='nfz_name',
            field=models.CharField(max_length=255, null=True, verbose_name='NFZ - nazwa'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(max_length=255, null=True, verbose_name='Telefon'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='position',
            field=models.CharField(max_length=255, null=True, verbose_name='Stanowisko (pracuje w)'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='profession',
            field=models.CharField(max_length=255, null=True, verbose_name='Zawód'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='religion',
            field=models.CharField(max_length=255, null=True, verbose_name='Religia'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='rights',
            field=models.CharField(max_length=255, null=True, verbose_name='Uprawnienia'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='shoe_size',
            field=models.CharField(max_length=255, null=True, verbose_name='Rozmiar buta'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='tax_number',
            field=models.CharField(max_length=255, null=True, verbose_name='Numer podatkowy'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=255, null=True, verbose_name='Użytkownik'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='work_clothes',
            field=models.CharField(max_length=255, null=True, verbose_name='Ubranie robocze'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='workplace',
            field=models.CharField(max_length=255, null=True, verbose_name='Miejsce pracy'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data rejestracji'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email'),
        ),
    ]
