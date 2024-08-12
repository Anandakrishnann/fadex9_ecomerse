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
        brand_name = request.POST.get('brand_name', '').strip()
        description = request.POST.get('description', '').strip()
        brand_image = request.FILES.get('brand_image')
        brand_status = request.POST.get('status') == 'on'

        
        if not brand_name or not description or not brand_image:
            messages.error(request, 'All fields are required.')
            return redirect('brand:brand_create')

        
        if Brand.objects.filter(brand_name__iexact=brand_name).exists():
            messages.error(request, f'The brand name "{brand_name}" already exists.')
            return redirect('brand:brand_create')

        
        brand = Brand.objects.create(
            brand_name=brand_name,
            brand_image=brand_image,
            description=description,
            status=brand_status
        )

        messages.success(request, 'Brand created successfully.')
        return redirect('brand:brand_list')
    
    
@method_decorator(admin_required, name='dispatch')

class BrandEdit(View):
    def get(self, request, pk):
        brands = get_object_or_404(Brand, id=pk)
        return render(request, 'Brands/brand_edit.html', {'brands': brands})

    def post(self, request, pk):
        brands = get_object_or_404(Brand, id=pk)
        brand_name = request.POST.get('brand_name', '').strip()
        description = request.POST.get('description', '').strip()
        brand_image = request.FILES.get('brand_image')
        brand_status = request.POST.get('status') == 'on'
        
        
        if brand_name != brands.brand_name and Brand.objects.filter(brand_name__iexact=brand_name).exists():
            messages.error(request, 'Brand with this name already exists.')
            return redirect('brand:brand_edit', pk=brands.id)

        
        if not brand_name or not description:
            messages.error(request, 'All fields are required.')
            return redirect('brand:brand_edit', pk=brands.id)
        
        brands.brand_name = brand_name
        brands.description = description
        brands.status = brand_status

        
        if brand_image:
            brands.brand_image = brand_image

        brands.save()
        messages.success(request, 'Brand edited successfully.')
        return redirect('brand:brand_list')

    
    
@method_decorator(admin_required, name='dispatch')
class BrandStatus(View):
    def get(self, request, pk):
        brand = get_object_or_404(Brand, id=pk)
        brand.status = not brand.status
        brand.save()
        messages.success(request, 'Status Changed Successfully')
        return redirect('brand:brand_list')