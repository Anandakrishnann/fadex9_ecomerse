from django.urls import path
from . views import *
from . import views

app_name = 'category'

urlpatterns = [
    path('create/',CreateCategory.as_view(),name='create_category'),
    path('category',CategoryList.as_view(),name='category'),
    path('edit/<int:pk>/',CategoryEdit.as_view(),name='edit_category'),
    path('delete/<int:pk>/',DeleteCategory.as_view(),name='delete_category'),
]
