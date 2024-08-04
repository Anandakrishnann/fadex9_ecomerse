from django.urls import path
from . views import *
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('login/',AdminLogin.as_view(),name='admin_login'),
    path('logout/',views.logout,name='admin_logout'),
    path('admin/',Admin.as_view(),name='admin_dash'),
    path('users/',AdminUsers.as_view(),name='admin_view'),
    path('reports/',SalesReport.as_view(),name='sales_report'),
    path('filter/',OrderDateFilter.as_view(),name='date_filter'),
    path('order_status/<int:pk>/',OrderStatus.as_view(), name='order_status'),
    path('user_block/<int:pk>/',UserBlock.as_view(),name='user_block'),
    path('user_delete/<int:pk>/',UserDelete.as_view(),name='user_delete'),
]
