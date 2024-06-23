from django.urls import path
from . views import *
from . import views

urlpatterns = [
    path('',Index_View.as_view(),name='home'),
    path('register/',Register_View.as_view(),name='register'),
    path('login/',Login_View.as_view(),name='login'),
    path('verify_otp/',Verify_Otp.as_view(),name='verify_otp'),
    path('resend_otp/',Resend_Otp.as_view(),name='resend_otp'),
    path('adminlogin/',Admin_Login.as_view(),name='adminlogin'),
    path('admindash/',Admin_View.as_view(),name='admindash'),
]
