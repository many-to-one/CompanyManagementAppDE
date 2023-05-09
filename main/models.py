from django.db import models

from users.models import CustomUser


class Work(models.Model):
    date = models.CharField(
        null=False,
        default='00-00-00',
        max_length=8,
        verbose_name='Data',
    )
    timestart = models.CharField(
        null=False,
        default='00:00',
        max_length=5,
        verbose_name='Początek',
    )
    timefinish = models.CharField(
        null=False,
        default='00:00',
        max_length=5,
        verbose_name='Koniec',
    )
    work_object = models.CharField(
        null=True,
        max_length=100,
        verbose_name='Miejsce pracy',
    )
    work_type = models.CharField(
        null=True,
        max_length=100,
        verbose_name='Czynność',
    )
    coffee_food = models.FloatField(
        null=True,
        default=0.00,
        verbose_name='Kawa/Posiłki',
    )
    fuel = models.FloatField(
        null=True,
        default=0.00,
        verbose_name='Paliwo',
    )
    prepayment = models.FloatField(
        null=True, 
        default=0.00,     
        verbose_name='Zaliczka',
    )
    phone_costs = models.FloatField(
        null=True,
        default=0.00,
        verbose_name='Telefon',
    )
    user = models.ManyToManyField(
        CustomUser
    )
