from typing import Iterable, Optional
from django.utils import timezone
from django.db import models
from django.urls import reverse
from datetime import datetime
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
    payment = models.CharField(
        null=True, 
        default=0.00,  
        max_length=100,   
        verbose_name='Kwota',
    )
    payment_hour = models.FloatField(
        default=0,
        verbose_name='Stawka za godzinę',
    )
    user = models.ManyToManyField(
        CustomUser
    )
    work_objects = models.ManyToManyField(
        'WorkObject'
    )

    def __str__(self) -> str:
        for user in self.user.all():
            return str(user.username)
    
    # def work_payment(self):
        # self.user = CustomUser.objects.get(id=pk)
        # self.payment * self.user.payment


class WorkObject(models.Model):
    name = models.CharField(
        null=True,
        max_length=150,
    )
    coffee_food = models.FloatField(
        null=True,
        default=0.00,
        # max_length=100,
        verbose_name='Kawa/Posiłki',
    )
    user = models.ManyToManyField(
        CustomUser,
    )

    def __str__(self):
        return str(self.id)
        

# class WorkObject(models.Model):
#     name = models.CharField(
#         null=True,
#         max_length=150,
#     )
#     coffee_food = models.FloatField(
#         null=True,
#         default=0.00,
#         # max_length=100,
#         verbose_name='Kawa/Posiłki',
#     )
#     user = models.ManyToManyField(
#         CustomUser,
#     )

#     def __str__(self):
#         return str(self.id)
    

class TotalWorkObject(models.Model):
    name = models.CharField(
        null=True,
        max_length=150,
    )
    obj_coffee_food = models.CharField(
        null=True,
        default=0.00,
        max_length=100,
        verbose_name='Kawa/Posiłki',
    )
    obj_fuel = models.CharField(
        null=True,
        default=0.00,
        max_length=100,
        verbose_name='Paliwo',
    )
    obj_prepayment = models.CharField(
        null=True,   
        default=0.00,
        max_length=100,   
        verbose_name='Zaliczka',
    )
    obj_phone_costs = models.CharField(
        null=True,
        default=0.00,
        max_length=100,
        verbose_name='Telefon',
    ) 
    work_object = models.ManyToManyField(
        WorkObject,
    )


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
    

class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
        )
    name = models.CharField(
        null=True,
        max_length=50,
    )
    work_object = models.ForeignKey(
        WorkObject,
        null=True, 
        on_delete=models.CASCADE, 
        related_name='objekt'
        )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    day = models.CharField(
        null=True,
        max_length=50,
    )
    time = models.CharField(
        null=True,
        max_length=50,
    )

    def __str__(self) -> str:
        return self.sender.username