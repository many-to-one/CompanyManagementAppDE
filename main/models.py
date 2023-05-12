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
    over_time = models.CharField(
        null=True,
        default='00:00',
        max_length=5,
        verbose_name='Nadgodziny',
    )
    sum_time_sec = models.FloatField(
        null=True,
        default=0.00,
        verbose_name='Czas pracy razem',
    )
    sum_over_time_sec = models.CharField(
        null=True,
        default='00:00',
        max_length=5,
        verbose_name='Nadgodziny',
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
    coffee_food = models.CharField(
        null=True,
        # default=0.00,
        max_length=100,
        verbose_name='Kawa/Posiłki',
    )
    fuel = models.CharField(
        null=True,
        # default=0.00,
        max_length=100,
        verbose_name='Paliwo',
    )
    prepayment = models.CharField(
        null=True, 
        # default=0.00,  
        max_length=100,   
        verbose_name='Zaliczka',
    )
    phone_costs = models.CharField(
        null=True,
        # default=0.00,
        max_length=100,
        verbose_name='Telefon',
    )
    user = models.ManyToManyField(
        CustomUser
    )
    work_objects = models.ManyToManyField(
        'WorkObject'
    )

    def __str__(self) -> str:
        return str(self.date)
    

class WorkObject(models.Model):
    name = models.CharField(
        null=True,
        max_length=150,
    )
    user = models.ManyToManyField(
        CustomUser,
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