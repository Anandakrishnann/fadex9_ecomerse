from django.urls import path
from . views import *
from . import views

app_name = 'user_panel'

urlpatterns = [
    path('create/',CreateAddress.as_view(),name='create_address'),
    path('edit/<int:pk>/',EditAddress.as_view(),name='edit_address'),
    path('details/<int:pk>/',EditDetails.as_view(),name='edit_details'),
    path('password_change',ChangePassword.as_view(),name='change_password'),
    path('add',AddAddress.as_view(),name='add_address'),
    path('user_dash',UserDashboard.as_view(),name='user_dash'),
    path('user_details',UserDetails.as_view(),name='user_details'),
    path('default/<int:pk>/',MakeAsDefault.as_view(),name='make_as_default'),
    path('delete/<int:pk>/',AddressDelete.as_view(),name='address_delete'),
    path('toggle-address-status/', ToggleAddressStatus.as_view(), name='toggle_address_status'),

    
]