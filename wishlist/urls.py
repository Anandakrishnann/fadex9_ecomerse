from django.urls import path
from . views import *
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('add-to-wishlist/', AddToWishlist.as_view(), name='add_to_wishlist'),  
    path('wishlist-to-cart/', WishlistToCart.as_view(), name='wishlist_to_cart'),  
    path('remove/<int:pk>/', RemoveWishlist.as_view(), name='remove_wishlist')
]
