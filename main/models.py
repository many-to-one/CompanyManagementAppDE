import json
from typing import Iterable, Optional
from django.utils import timezone
from django.db import models
from django.urls import reverse
from datetime import datetime
from users.models import CustomUser
    

class Work(models.Model):
    date = models.CharField(
        null=False,
        default='00-00-00',
        max_length=8,
        verbose_name='Data',
    )
    username = models.CharField(
        null=True,
        max_length=125,
        verbose_name='Imię użytkownika',
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
        CustomUser,
    )
    work_objects = models.ManyToManyField(
        'WorkObject'
    )

    def __str__(self) -> str:
        return self.work_object

    # def __str__(self) -> str:
    #     for user in self.user.all():
    #         return str(user.username)
    
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
    

class Task(models.Model):
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        CustomUser, 
        related_name='wyconawca',
        on_delete=models.SET_NULL, ## It helps to protect the task after the User will be deleted
        null=True,
    )
    username = models.CharField(
        null=True,
        max_length=150,
    )
    work_object = models.ForeignKey(
        WorkObject, 
        related_name='object',
        on_delete=models.CASCADE
    )
    content = models.CharField(
        null=True,
        max_length=250,
    )
    done = models.BooleanField(
        default=False
    )

    def __str__(self) -> str:
        return self.username
    

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
        CustomUser,
    )

    def __str__(self):
        return str(self.name)
    

class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser, 
        related_name='nadawca',
        on_delete=models.SET_NULL, ## It helps to protect the message after the User will be deleted
        null=True,
        )
    name = models.CharField(
        null=True,
        max_length=50,
    )
    work_object = models.ForeignKey(
        WorkObject,
        null=True, 
        on_delete=models.PROTECT, 
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
    for_sender_is_read = models.BooleanField(
        default=False
    )
    for_recipient_is_read = models.BooleanField(
        default=False
    )

    # def set_data(self, data):
    #     self.recipient = json.dumps(data)

    # def get_data(self):
    #     return json.loads(self.recipient)

    def __str__(self) -> str:
        return self.name
    

class IsRead(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE, 
        null=True,
    )
    username = models.CharField(
        null=True,
        max_length=50,
    )
    work_object = models.ForeignKey(
        WorkObject,
        null=True, 
        on_delete=models.CASCADE, 
        )
    is_read = models.BooleanField(
        default=False,
    )
    
    def __str__(self):
        return str(self.id)
    

class Vacations(models.Model):
    user = models.ForeignKey(
        CustomUser, 
        related_name='user',
        on_delete=models.CASCADE,
        null=True,
        )
    year = models.CharField(
        default='0000',
        max_length=4,
        verbose_name='Rok',
    )
    date = models.CharField(
        default='00-00-0000',
        max_length=10,
        verbose_name='Data',
    )
    v_from = models.CharField(
        default='00-00-0000',
        max_length=10,
        verbose_name='Od',
    )
    v_to = models.CharField(
        default='00-00-0000',
        max_length=10,
        verbose_name='Do',
    )
    type = models.CharField(
        null=True,
        max_length=50,
        verbose_name='Typ urlopu',
    )
    actually_days_to_use = models.IntegerField(
        default=0,
        verbose_name='Faktyczny urlop według przepracowanych dni',
    )
    days_used_in_current_year = models.IntegerField(
        default=0,
        verbose_name='Użyto w bieżącym roku',
    )
    days_to_use_in_last_year = models.IntegerField(
        default=0,
        verbose_name='Do użycia w poprzednim roku',
    )
    days_used_in_last_year = models.IntegerField(
        default=0,
        verbose_name='Użyto w poprzednim roku',
    )
    days_planned = models.IntegerField(
        null=True,
        verbose_name='Zaplanowany urlop',
    )
    consideration = models.BooleanField(
        default=False,
        verbose_name='Rozpatrywanie',
    )
    accepted = models.BooleanField(
        default=False,
        verbose_name='Akceptacja',
    )

    def __str__(self) -> str:
        return self.user.username
    

class VacationRequest(models.Model):
    v_request = models.ForeignKey(
        Vacations,
        on_delete=models.CASCADE, 
    )

    def __str__(self) -> str:
        return self.v_request.date