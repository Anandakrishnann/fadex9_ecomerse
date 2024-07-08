from django.urls import path
from . views import *
from . import views

app_name = 'product'

urlpatterns = [
    path('create/', ProductCreate.as_view(), name='product_create'),
    path('products', ProductView.as_view(), name='products'),
    path('info/<int:pk>/', ProductInfo.as_view(), name='product_info'),
    path('edit/<int:pk>/', ProductEdit.as_view(), name='product_edit'),
    path('image/<int:pk>/', ProductImage.as_view(), name='product_image'),
    path('variants/<int:pk>/', ProductVariants.as_view(), name='product_variant'),
    path('stocks/<int:pk>/', ProductStocks.as_view(), name='product_stocks'),
    path('review/<int:pk>/', Reviews.as_view(), name='product_review'),
    path('delete/<int:pk>/', ProductDelete.as_view(), name='product_delete'),
    path('image_delete/<int:pk>/', DeleteImage.as_view(), name='image_delete'),
    path('review_delete/<int:pk>/', DeleteReview.as_view(), name='review_delete'),
]   