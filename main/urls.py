from django.urls import path

from .views import *

urlpatterns = [
    path('home/', index, name='home'),
    path('user_work/<pk>/', userWork, name='user_work'),
    path('create_work_object/', WorkObjects.as_view(), name='work_objects'),
    path('create_work_object/', createWorkObject, name='create_work_object'),
    path('work_object/<pk>/', WorkObjectView.as_view(), name='work_object'),
    path('raport/<user_pk>/', getRaport, name='raport'),
    ]