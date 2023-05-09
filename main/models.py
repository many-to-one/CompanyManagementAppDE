from django.db import models


class Work(models.Model):
    date = models.CharField(
        default='00-00-00',
        max_length=8,
    )
    timestart = models.CharField(
        default='00:00',
        max_length=5,
    )
    timefinish = models.CharField(
        default='00:00',
        max_length=5,
    )
