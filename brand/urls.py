from django.urls import path
from . views import *
from . import views

app_name = 'brand'

urlpatterns = [
    path('create/',BrandCreate.as_view(),name='brand_create'),
    path('brand/',BrandList.as_view(),name='brand_list'),
    path('edit/<int:pk>/',BrandEdit.as_view(),name='brand_edit'),
    path('status/<int:pk>/',BrandStatus.as_view(),name='brand_status'),

]
