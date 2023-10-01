from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .manager import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    acceptation = models.BooleanField(
        _('Zatwierdź'),
        default=False,
    )
    administrator = models.CharField(
        _('Administrator'),
        null=True,
        max_length= 255,
    )
    username = models.CharField(
        _('Użytkownik'),
        null=True,
        max_length= 255,
        )
    email = models.EmailField(_("email"), unique=True)
    fp_token = models.CharField(
        null=True,
        max_length=192,
        unique=True,
    )
    token_expiration = models.DateTimeField(
        _('Czas życia tokena'),
        null=True,
        blank=True,
    )
    ip_address = models.JSONField(
        null=True,
    )
    birthday = models.CharField(
        _('Data urodzenia'),
        null=True,
        max_length= 55,
        )
    birthplace = models.CharField(
        _('Miejsce urodzenia'),
        null=True,
        max_length= 255,
        )
    workplace = models.CharField(
        _('Miejsce pracy'),
        null=True,
        max_length= 255,
        )
    religion = models.CharField(
        _('Religia'),
        null=True,
        max_length= 255,
        )
    insurance_number = models.CharField(
        _('Numer ubezpieczenia'),
        null=True,
        max_length= 255,
        )
    tax_number = models.CharField(
        _('Numer podatkowy'),
        null=True,
        max_length= 255,
        )
    adress_pl = models.CharField(
        _('Adres w Polsce'),
        null=True,
        max_length= 255,
        )
    adress_de = models.CharField(
        _('Adres w Niemczech'),
        null=True,
        max_length= 255,
        )
    profession = models.CharField(
        _('Zawód'),
        null=True,
        max_length= 255,
        )
    position = models.CharField(
        _('Stanowisko (pracuje w)'),
        null=True,
        max_length= 255,
        )
    internal_tax_number = models.CharField(
        _('Wewnętrzny numer podatkowy'),
        null=True,
        max_length= 255,
        )
    nfz_name = models.CharField(
        _('NFZ - nazwa'),
        null=True,
        max_length= 255,
        )
    nfz_adress = models.CharField(
        _('NFZ - adres'),
        null=True,
        max_length= 255,
        )
    phone_number = models.CharField(
        _('Telefon'),
        null=True,
        max_length= 255,
        )
    bank = models.CharField(
        _('Nazwa banku'),
        null=True,
        max_length= 255,
        )
    bic_swift = models.CharField(
        _('BIC/SWIFT'),
        null=True,
        max_length= 255,
        )
    bank_account = models.CharField(
        _('Konto i właściciel'),
        null=True,
        max_length= 255,
        )
    health_insurance_de = models.CharField(
        _('Ubezpieczenie w Niemczech'),
        null=True,
        max_length= 255,
        )
    health_insurance_de_number = models.CharField(
        _('KK VersNr'),
        null=True,
        max_length= 255,
        )
    shoe_size = models.CharField(
        _('Rozmiar buta'),
        null=True,
        max_length= 255,
        )
    growth = models.CharField(
        _('Wzrost'),
        null=True,
        max_length= 255,
        )
    work_clothes = models.CharField(
        _('Ubranie robocze'),
        null=True,
        max_length= 255,
        )
    rights = models.CharField(
        _('Uprawnienia'),
        null=True,
        max_length= 255,
        )
    payment = models.FloatField(
        _('Stawka za godzinę'),
        null=True,
        default=0,
    )
    vacations_days_quantity = models.IntegerField(
        _('Ilość przysługujących dni urlopu'),
        default=0,
    )
    vacations_days_quantity_de = models.IntegerField(
        _('Ilość przysługujących dni urlopu'),
        default=0,
    )
    vacacions_on_demand = models.IntegerField(
        _('Ilość dni urlopu na żądanie'),
        default=4,
    )
    cares_vacations = models.IntegerField(
        _('Ilość dni urlopu opiekuńczego'),
        default=5,
    )
    force_majeure_vacations = models.IntegerField(
        _('Ilość godzin urlopu z powodu siły wyższej'),
        default=16,
    )
    compassionate_vacations = models.IntegerField(
        _('Ilość dni urlopu okolicznościowego'),
        default=2,
    )
    last_year_vacations_days_quantity = models.IntegerField(
        _('Ilość przysługujących dni urlopu za zeszły rok'),
        default=0,
    )
    last_year_vacations_days_quantity_de = models.IntegerField(
        _('Ilość przysługujących dni urlopu za zeszły rok'),
        default=0,
    )
    days_to_use_in_current_year = models.IntegerField(
        _('Do użycia w bieżącym roku'),
        default=0,
    )
    days_to_use_in_current_year_de = models.IntegerField(
        _('Do użycia w bieżącym roku'),
        default=0,
    )
    is_logged = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(
        _('Data rejestracji'),
        default=timezone.now,
        )

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        if self.username:
            return self.username
        else:
            return self.email
        
    
    def get_absolute_url(self):
        return reverse(
            'user',
            kwargs={'pk': str(self.id)}
        )
    

class BlacklistToken(models.Model):
    date = models.DateTimeField(
        _('Data'),
        null=True,
        blank=True,
    )
    token = models.CharField(
        max_length=192, 
        unique=True
    )
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.blacklisted_at)[:20]
    

class IPAddressList(models.Model):
    username = models.CharField(
        max_length=250, 
        null=True,
    )
    ip_address = models.CharField(
        max_length=1000, 
        null=True,
    )
    blocked = models.BooleanField(
        default=False,
    )


    def __str__(self):
        return str(self.ip_address)