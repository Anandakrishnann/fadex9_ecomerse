from django.urls import path
from . views import *
from . import views

app_name = 'cart'

urlpatterns = [
    path('add-to-cart/', AddToCart.as_view(), name='add_to_cart'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart_delete/<int:pk>/', CartItemsDelete.as_view(), name='delete_cart'),
    path('update_cart_item_quantity/', UpdateCartItemQuantity.as_view(), name='update_cart_item_quantity'),
]
