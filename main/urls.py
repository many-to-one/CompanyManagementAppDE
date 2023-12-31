from django.urls import path
from .views_.excel import raportsToExcel, vacationsToExcel
from .views_.vacations import(
    addVacation,
    allVacationRequests,
    delete_vacations,
    delete_vacations_question,
    deleteVacation,
    deleteVacationPage,
    deleteVacationRequest,
    deleteVacationRequestQuestion,
    editVacation,
    vacationRequest,
    vacations,
    vacationsExcelPage,
) 
from .views_.documents import deleteDocument, getDocuments, upload_document
from .views_.messages import (
    chat, 
    chek_messages, 
    chek_messages_user, 
    deleteAllMessagesWO, 
    deleteMessConf, 
    deleteQuestionMessages, 
    showCount, 
    showCountAll, 
    showMessageHistory
)
from .views_.schedule import schedule
from .views_.header_activity import header
from .views_.tasks_view import (
    deleteAllDoneTasksQuestion, 
    deleteTask, 
    deleteTaskQuestion, 
    doneTask, 
    new_task, 
    task, 
    taskQuantity
)
from .views_.subcontractor import addSubcontractor, deleteSubcontractor
from .views_.work_object_view import (
    deleteUserFromObject, 
    deleteUserFromObjectQuestion, 
    workObjectView
)
from .views_.work_objects import WorkObjects, changeStatusWorkObject, deleteWorkObject, deleteWorkObjectQuestion
from .views_.create_update_workobject import createWorkObject, updateWorkObject
from .views_.delete_user_work import (
    deleteUserWork, 
    deleteListUserWork, 
    deleteListUserWorkQuestion, 
    success_delete_user_work
)
from .views_.user_raport import getUserRaport
from .views_.raports import raports
from .views_.work_object_raport import workObjectRaport
from .views_.delete_user_work_question import deleteUserWorkQuastion
from .views_.update_user_work import updateUserWork
from . views import *
from .views_.user_work import userWork


urlpatterns = [
    path('header/', header, name='header'),
    path('', index, name='home'),
    path('user_work/<pk>/', userWork, name='user_work'),
    path('update_user_work/<work_pk>/', updateUserWork, name='update_user_work'),
    path('deleteUserWorkQuastion/<work_pk>/', deleteUserWorkQuastion, name='deleteUserWorkQuastion'),
    path('deleteUserWork/<work_pk>/', deleteUserWork, name='deleteUserWork'),
    path('success_delete_user_work/<work_date>/', success_delete_user_work, name='success_delete_user_work'),
    path('deleteListUserWorkQuestion/', deleteListUserWorkQuestion, name='deleteListUserWorkQuestion'),
    path('deleteListUserWork/', deleteListUserWork, name='deleteListUserWork'),
    path('work_objects/', WorkObjects, name='work_objects'),
    path('create_work_object/', createWorkObject, name='create_work_object'),
    path('updateWorkObject/<pk>/', updateWorkObject, name='updateWorkObject'),
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
    path('deleteMessConf/', deleteMessConf, name='deleteMessConf'),
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
    path('showMessageHistory/<pk>/', showMessageHistory, name='showMessageHistory'),
    path('chek_messages_user', chek_messages_user, name='chek_messages_user'),
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
    path('upload_document/', upload_document, name='upload_document'),
    path('getDocuments/<pk>/', getDocuments, name='getDocuments'),
    path('deleteDocument/', deleteDocument, name='deleteDocument'),
    path('getWarehouse/', getWarehouse, name='getWarehouse'),
    path('editValue/', editValue, name='editValue'),
    path('deleteValue/', deleteValue, name='deleteValue'),
    path('newValue/', newValue, name='newValue'),
    path('getSearch/', getSearch, name='getSearch'),
    path('resetWarehouse/', resetWarehouse, name='resetWarehouse'),
    path('imageWarehouse/', imageWarehouse, name='imageWarehouse'),
]