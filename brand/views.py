from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from utils.decorators import admin_required


# Create your views here.


@method_decorator(admin_required, name='dispatch')
class BrandList(View):
    def get(self, request):
        if request.user.is_authenticated:
            query = request.GET.get('q')
            if query:
                brands = Brand.objects.filter(brand_name__icontains=query)
            else:
                brands = Brand.objects.all()
            return render(request, 'Brands/brand.html',{'brands':brands})
        else:
            return render(request, 'Admin_panel/admin_side/admin_login.html')
    
@method_decorator(admin_required, name='dispatch')
class BrandCreate(View):
    def get(self, request):
        return render(request, 'Brands/brand_create.html')
    
    def post(self, request):
        if request.method == 'POST':
            brand_name = request.POST.get('brand_name')
            description = request.POST.get('description', '')
            brand_image = request.FILES.get('brand_image')
            brand_status = request.POST.get('status') == 'on'
            
            if brand_name and brand_image:
                brand = Brand.objects.create(
                    brand_name=brand_name,
                    brand_image=brand_image,
                    description=description,
                    status=brand_status
                )
                
                brand.save()
                return redirect('brand:brand_list')
        return render(request, 'Brands/brand_create.html')
@method_decorator(admin_required, name='dispatch')
class BrandEdit(View):
    def get(self, request, pk):
        brands = get_object_or_404(Brand, id=pk)
        return render(request, 'Brands/brand_edit.html', {'brands': brands})

    def post(self, request, pk):
        brands = get_object_or_404(Brand, id=pk)
        brand_name = request.POST.get('brand_name')
        description = request.POST.get('description', '')
        brand_image = request.FILES.get('brand_image')
        brand_status = request.POST.get('status') == 'on'
        
        # Check if the new brand name is unique and not the same as the current brand
        if brand_name != brands.brand_name and Brand.objects.filter(brand_name=brand_name).exists():
            messages.error(request, 'Brand with this name already exists.')
        else:
            brands.brand_name = brand_name
            brands.description = description
            brands.status = brand_status
            if brand_image:
                brands.brand_image = brand_image
            
            brands.save()
            return redirect('brand:brand_list')
        
        return render(request, 'Brands/brand_edit.html', {'brands': brands})
    
    
@method_decorator(admin_required, name='dispatch')
class BrandStatus(View):
    def get(self, request, pk):
        brand = get_object_or_404(Brand, id=pk)
        brand.status = not brand.status
        brand.save()
        return redirect('brand:brand_list')