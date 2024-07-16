from django.urls import path
from . views import *
from . import views

app_name = 'cart'

urlpatterns = [
    path('add-to-cart/', AddToCart.as_view(), name='add_to_cart'),
    path('cart-view/', CartView.as_view(), name='cart_view'),
    path('cart-checkout/', CartCheckout.as_view(), name='cart_checkout'),
    path('cart-delete/<int:pk>/', CartItemsDelete.as_view(), name='delete_cart'),
    path('update-cart-quantity/',views.update_cart_quantity, name='update_cart_quantity'),
    path('update-cart-status/', UpdateCartStatus.as_view(), name='update_cart_status'),
]
