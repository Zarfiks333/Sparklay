from django.urls import path
from user.views import *

app_name = 'user'

urlpatterns = [
    path('accounts/login/', loginOrSingIn, name='loginOrSingIn'),
    path('accounts/register/', register, name='register'),
    path('accounts/logout/', logout , name='logout'),
    path('confirm-email/<str:token>/', confirm_email, name='confirm_email'),
    path('verify-code/', verify_code, name='verify_code'),
    path('password_reset/', password_reset, name='password_reset'),
    path('password_reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
]
