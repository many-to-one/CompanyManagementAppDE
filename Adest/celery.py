from __future__ import absolute_import, unicode_literals
import os
import time
from celery import Celery
from django.conf import settings
import logging

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Adest.settings')

app = Celery('Adest')

# Configure Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.brocker_url = settings.CELERY_BROKER_URL

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)