from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .manager import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('Użytkownik'),
        null=True,
        max_length= 255,
        )
    email = models.EmailField(_("email"), unique=True)
    fp_token = models.CharField(
        null=True,
        max_length=110,
        unique=True,
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
    # work_objects = models.ManyToManyField(
    #     WorkObject
    # )
    # work_type = models.ManyToManyField(
    #     WorkType
    # )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(
        _('Data rejestracji'),
        default=timezone.now,
        )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    def get_absolute_url(self):
        return reverse(
            'user',
            kwargs={'pk': str(self.id)}
        )