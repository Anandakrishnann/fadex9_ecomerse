from django.urls import path
from . views import *
from . import views

app_name = 'user_panel'

urlpatterns = [
    path('create/',Address.as_view(),name='address'),
    
]