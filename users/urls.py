from django.urls import path

from .views import *

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('user/<pk>/', Profile, name='user'),
    path('forgot_password/', forgotPassword, name='forgot_password'),
    path('change_password/<token>/<uidb64>/', changePassword, name='change_password'),
    path('all_users/', AllUsers, name='all_users'),
    ]