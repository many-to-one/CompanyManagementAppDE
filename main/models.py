from django.db import models
from django.urls import reverse

from users.models import CustomUser

# from users.models import CustomUser


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
    diff_time = models.CharField(
        null=True,
        default='00:00',
        max_length=5,
        verbose_name='Czas pracy',
    )
    sum_time_sec = models.FloatField(
        null=True,
        default=0.00,
        verbose_name='Czas pracy razem',
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

    def __str__(self) -> str:
        return str(self.date)
    

class WorkObject(models.Model):
    name = models.CharField(
        null=True,
        max_length=150,
    )
    user = models.ManyToManyField(
        CustomUser
    )

    def __str__(self):
        return str(self.name)


class WorkType(models.Model):
    name = models.CharField(
        null=True,
        max_length=150,
    )
    user = models.ManyToManyField(
        CustomUser
    )

    def __str__(self):
        return str(self.name)