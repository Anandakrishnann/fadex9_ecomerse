from django.urls import path
from . views import *
from . import views

app_name = 'coupon'

urlpatterns = [
    path('create_coupon/', CouponCreate.as_view(), name='create_coupon'),
    path('coupon/', CouponView.as_view(), name='coupon'),
    path('edit_coupon/<str:pk>/', EditCoupon.as_view(), name='edit_coupon'),
    path('coupon_status/<str:pk>/', CouponStatus.as_view(), name='coupon_status'),
]
