"""
URL configuration for FADEX9 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib import admin 
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Accounts.urls')),  # Main app
    path('admin_panel/', include('admin_panel.urls')),  # Admin panel app
    path('category/', include('category.urls')),  # Admin panel app
    path('products/', include('products.urls')),  # Admin panel app
    path('brands/', include('brand.urls')),  # Admin panel app
    path('user_panel/', include('user_panel.urls')),  # Admin panel app
    path('cart/', include('cart.urls')),  # Admin panel app
    path('auth/', include('social_django.urls', namespace='social')),
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
