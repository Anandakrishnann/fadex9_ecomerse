from django.urls import path
from . views import *
from . import views

urlpatterns = [
    path('',Admin_Login.as_view(),name='admin_login'),
    path('admin_view/',Admin_Users.as_view(),name='admin_view'),
    path('create_user/',Create_User.as_view(),name='create_user'),
    path('admin_dash/',Admin_dash.as_view(),name='admin_dash'),
    path('user_block/<int:pk>/',User_Block.as_view(),name='user_block'),
    path('user_delete/<int:pk>/',User_Delete.as_view(),name='user_delete'),
    
]
