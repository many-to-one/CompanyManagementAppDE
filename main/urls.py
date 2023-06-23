from django.urls import path

from .views import *

urlpatterns = [
    path('home/', index, name='home'),
    path('user_work/<pk>/', userWork, name='user_work'),
    path('update_user_work/<work_pk>/', updateUserWork, name='update_user_work'),
    path('work_objects/', WorkObjects, name='work_objects'),
    path('create_work_object/', createWorkObject, name='create_work_object'),
    path('work_object/<pk>/', workObjectView, name='work_object'),
    path('user_raport/<user_pk>/', getUserRaport, name='user_raport'),
    path('workobject_raport/<user_pk>/<object_pk>/', workObjectRaport, name='workobject_raport'),
    path('raports/', raports, name='raports'),
    path('chat/<pk>/', chat, name='chat'),
    path('vacations/<pk>/', vacations, name='vacations'),
    path('delete_vacations_requests_question/', delete_vacations_requests_question, name='delete_vacations_requests_question'),
    path('delete_vacations_requests/', delete_vacations_requests, name='delete_vacations_requests'),
    path('addVacation/', addVacation, name='addVacation'),
    path('editVacation/<pk>/', editVacation, name='editVacation'),
    path('deleteVacationPage/<pk>/', deleteVacationPage, name='deleteVacationPage'),
    path('deleteVacation/<pk>/', deleteVacation, name='deleteVacation'),
    path('allVacationRequests/', allVacationRequests, name='allVacationRequests'),
    path('vacationRequest/<pk>/', vacationRequest, name='vacationRequest'),
]