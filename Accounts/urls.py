from django.urls import path
from . views import *
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('products/<int:pk>/', ProductView.as_view(), name='product_details'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', views.logout, name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('shop/', ProductShop.as_view(), name='product_shop'),
    path('verify_otp/', VerifyOtp.as_view(), name='verify-otp'),
    path('resend_otp/', ResendOtp.as_view(), name='resend-otp'),
    path('contact/', Contact.as_view(), name='contact'),
    path('about/', About.as_view(), name='about'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset-done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
]