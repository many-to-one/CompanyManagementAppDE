from django.urls import path

from .views import *

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('user/<pk>/', Profile.as_view(), name='user'),
    ]