from django.urls import path

from .views import *

urlpatterns = [
    path('header/', header, name='header'),
    path('home/', index, name='home'),
    path('user_work/<pk>/', userWork, name='user_work'),
    path('update_user_work/<work_pk>/', updateUserWork, name='update_user_work'),
    path('deleteUserWorkQuastion/<work_pk>/', deleteUserWorkQuastion, name='deleteUserWorkQuastion'),
    path('deleteUserWork/<work_pk>/', deleteUserWork, name='deleteUserWork'),
    path('success_delete_user_work/<work_date>/', success_delete_user_work, name='success_delete_user_work'),
    path('deleteListUserWorkQuestion/', deleteListUserWorkQuestion, name='deleteListUserWorkQuestion'),
    path('deleteListUserWork/', deleteListUserWork, name='deleteListUserWork'),
    path('work_objects/', WorkObjects, name='work_objects'),
    path('create_work_object/', createWorkObject, name='create_work_object'),
    path('work_object/<pk>/', workObjectView, name='work_object'),
    path('addSubcontractor/<pk>/', addSubcontractor, name='addSubcontractor'),
    path('deleteSubcontractor/', deleteSubcontractor, name='deleteSubcontractor'),
    path('changeStatusWorkObject/<pk>/', changeStatusWorkObject, name='changeStatusWorkObject'),
    path('task/', task, name='task'),
    path('new_task/', new_task, name='new_task'),
    path('taskQuantity/', taskQuantity, name='taskQuantity'),
    path('doneTask/', doneTask, name='doneTask'),
    path('deleteTaskQuestion/', deleteTaskQuestion, name='deleteTaskQuestion'),
    path('deleteTask/', deleteTask, name='deleteTask'),
    path('deleteQuestionMessages/', deleteQuestionMessages, name='deleteQuestionMessages'),
    path('deleteAllMessagesWO/', deleteAllMessagesWO, name='deleteAllMessagesWO'),
    path('schedule/', schedule, name='schedule'),
    path('deleteAllDoneTasksQuestion/', deleteAllDoneTasksQuestion, name='deleteAllDoneTasksQuestion'),
    path('deleteUserFromObjectQuestion/<user_pk>/<work_object_pk>/', deleteUserFromObjectQuestion, name='deleteUserFromObjectQuestion'),
    path('deleteUserFromObject/<user_pk>/<work_object_pk>/', deleteUserFromObject, name='deleteUserFromObject'),
    path('deleteWorkObjectQuestion/<work_object_pk>/', deleteWorkObjectQuestion, name='deleteWorkObjectQuestion'),
    path('deleteWorkObject/<work_object_pk>/', deleteWorkObject, name='deleteWorkObject'),
    path('user_raport/<user_pk>/', getUserRaport, name='user_raport'),
    path('workobject_raport/<user_pk>/<object_pk>/', workObjectRaport, name='workobject_raport'),
    path('raports/', raports, name='raports'),
    path('showCount/<work_object_pk>/', showCount, name='showCount'),
    path('showCountAll/', showCountAll, name='showCountAll'),
    path('chat/<pk>/', chat, name='chat'),
    path('chek_messages/<pk>/', chek_messages, name='chek_messages'),
    path('vacations/<pk>/', vacations, name='vacations'), #1776
    path('delete_vacations_question/', delete_vacations_question, name='delete_vacations_question'),
    path('delete_vacations/', delete_vacations, name='delete_vacations'),
    path('vacationsExcelPage/', vacationsExcelPage, name='vacationsExcelPage'),
    path('vacationsToExcel/', vacationsToExcel, name='vacationsToExcel'),
    path('raportsToExcel/', raportsToExcel, name='raportsToExcel'),
    path('addVacation/', addVacation, name='addVacation'),
    path('editVacation/<pk>/', editVacation, name='editVacation'),
    path('deleteVacationPage/<pk>/', deleteVacationPage, name='deleteVacationPage'),
    path('deleteVacation/<pk>/', deleteVacation, name='deleteVacation'),
    path('allVacationRequests/', allVacationRequests, name='allVacationRequests'),
    path('vacationRequest/<pk>/', vacationRequest, name='vacationRequest'),
    path('deleteVacationRequestQuestion/', deleteVacationRequestQuestion, name='deleteVacationRequestQuestion'),
    path('deleteVacationRequest/', deleteVacationRequest, name='deleteVacationRequest'),
]