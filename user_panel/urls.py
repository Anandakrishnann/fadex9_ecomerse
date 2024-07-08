from django.urls import path
from . views import *
from . import views

app_name = 'user_panel'

urlpatterns = [
    path('create/',CreateAddress.as_view(),name='create_address'),
    path('edit/<int:pk>/',EditAddress.as_view(),name='edit_address'),
    path('user_dash',UserDashboard.as_view(),name='user_dash'),
    path('default/<int:pk>/',MakeAsDefault.as_view(),name='make_default'),
    path('delete/<int:pk>/',AddressDelete.as_view(),name='address_delete')
]