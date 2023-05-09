from django.urls import path

from .views import *

urlpatterns = [
    path('home/', index, name='home'),
    path('user_work/<pk>/', userWork, name='user_work'),
    ]