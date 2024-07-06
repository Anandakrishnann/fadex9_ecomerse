from django.urls import path
from . views import *
from . import views

app_name = 'accounts'

urlpatterns = [
    path('',IndexView.as_view(),name='home'),
    path('products/<int:pk>/',ProductView.as_view(),name='product_details'),
    path('register/',RegisterView.as_view(),name='register'),
    path('logout/',views.logout,name='logout'),
    path('login/',LoginView.as_view(),name='login'),
    path('verify_otp/',VerifyOtp.as_view(),name='verify-otp'),
    path('resend_otp/',ResendOtp.as_view(),name='resend-otp'),
]
