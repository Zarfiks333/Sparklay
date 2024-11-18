from django.urls import path
from main.views import *

app_name = 'main'

urlpatterns = [
    path('', indexView, name='index'),
    path('channels/', mainView, name='mainView'),
]
