from django.urls import path
from . views import *
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('login/',AdminLogin.as_view(),name='admin_login'),
    path('logout/',views.logout,name='admin_logout'),
    path('admin/',AdminDash.as_view(),name='admin_dash'),
    path('best_products/',BestSellingProducts.as_view(),name='best_selling_product'),
    path('best_category/',BestSellingCategory.as_view(),name='best_selling_category'),
    path('best_brand/',BestSellingBrands.as_view(),name='best_selling_brand'),
    path('users/',AdminUsers.as_view(),name='admin_view'),
    path('reports/',SalesReport.as_view(),name='sales_report'),
    path('filter/',OrderDateFilter.as_view(),name='date_filter'),
    path('order_status/<int:pk>/',OrderStatus.as_view(), name='order_status'),
    path('user_block/<int:pk>/',UserBlock.as_view(),name='user_block'),
    path('user_delete/<int:pk>/',UserDelete.as_view(),name='user_delete'),
]
