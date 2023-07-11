from django.urls import path

from .views import *

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('block_ip_address/<token>/<uidb64>/', block_ip_address, name='block_ip_address'),
    path('accept_ip_address/<token>/<uidb64>/', accept_ip_address, name='accept_ip_address'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('chack_email/', chack_email, name="chack_email"),
    path('user/<pk>/', Profile, name='user'),
    path('forgot_password/', forgotPassword, name='forgot_password'),
    path('change_password/<token>/<uidb64>/', changePassword, name='change_password'),
    path('all_users/', AllUsers, name='all_users'),
    path('deleteQuestion/<pk>/', deleteQuestion, name='deleteQuestion'),
    path('deleteUser/<pk>/<user>/', deleteUser, name='deleteUser'),
    ]