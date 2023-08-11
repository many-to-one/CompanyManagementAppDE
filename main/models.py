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
        max_length=20,
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
    sum_over_time_sec = models.FloatField(
        null=True,
        default=0.00,
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
    coffee_food = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Kawa/Posiłki',
    )
    fuel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Paliwo',
    )
    prepayment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Zaliczka',
    )
    phone_costs = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Telefon',
    )
    payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Kwota',
    )
    payment_hour = models.FloatField(
        default=0.00,
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
    message_count = models.IntegerField(
        default=0
    )

    def __str__(self):
        return str(self.id)
    

class Task(models.Model):
    date_obj = models.DateTimeField(default=timezone.now) ## For sorted dates
    date = models.CharField(
        null=True,
        max_length=15,
        verbose_name='Data',
    )
    abbreviated_month = models.CharField(
        null=True,
        max_length=5,
        verbose_name='Miesiąc',
    )
    user = models.ForeignKey(
        CustomUser, 
        related_name='wyconawca',
        on_delete=models.SET_NULL, ## It helps to protect the task after the User will be deleted
        null=True,
        verbose_name='Użytkownik',
    )
    username = models.CharField(
        null=True,
        max_length=150,
        verbose_name='Imię',
    )
    work_object = models.ForeignKey(
        WorkObject, 
        related_name='object',
        on_delete=models.CASCADE,
        verbose_name='Objekt',
    )
    content = models.CharField(
        null=True,
        max_length=500,
        verbose_name='Treść',
    )
    done = models.BooleanField(
        default=False,
        verbose_name='Wykonano',
    )

    # def formatted_date(self) :
    #     return self.date.strftime('%d %B %Y')

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
        # on_delete=models.CASCADE,
        on_delete=models.SET_NULL,
        null=True,
        )
    username = models.CharField(
        null=True,
        max_length=50,
        verbose_name='Imię użytkownika',
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
        return str(self.id)
    

class VacationRequest(models.Model):
    v_request = models.ForeignKey(
        Vacations,
        on_delete=models.CASCADE, 
    )

    def __str__(self) -> str: 
        return self.v_request.date