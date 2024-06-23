from django.urls import path
from . views import *
from . import views

urlpatterns = [
    path('',Index_View.as_view(),name='home'),
    path('register/',Register_View.as_view(),name='register'),
    path('login/',Login_View.as_view(),name='login'),
    path('verify-otp/',Verify_Otp.as_view(),name='verify-otp'),
    path('resend-otp/',Resend_Otp.as_view(),name='resend-otp'),
    path('admin-login/',Admin_Login.as_view(),name='admin-login'),
    path('admin-dash/',Admin_View.as_view(),name='admin-dash'),
]
