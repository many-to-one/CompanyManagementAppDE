from django.urls import path

from .views import *

urlpatterns = [
    path('home/', index, name='home'),
    path('user_work/<pk>/', userWork, name='user_work'),
    path('create_work_object/work_objects', WorkObjects.as_view(), name='work_objects'),
    path('create_work_object/', CreateWorkObject, name='create_work_object'),
    path('work_object/<pk>/', WorkObjectView.as_view(), name='work_object'),
    ]