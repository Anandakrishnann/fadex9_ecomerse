from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.views import View

# Create your views here.

class BrandList(View):
    def get(self, request):
        brands = Brand.objects.all()
        return render(request, 'Brands/brand.html',{'brands':brands})
    

class BrandCreate(View):
    def get(self, request):
        return render(request, 'Brands/brand_create.html')
    
    def post(self, request):
        if request.method == 'POST':
            brand_name = request.POST.get('brand_name')
            description = request.POST.get('description', '')
            brand_image = request.FILES.get('brand_image')
            brand_status = request.POST.get('status', False) == 'on'
            
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

        

class BrandEdit(View):
    def get(self, request, pk):
        brands = get_object_or_404(Brand, id=pk)
        return render(request, 'Brands/brand_edit.html',{'brands':brands})

    def post(self, request, pk):
        brand_name = request.POST['brand_name']
        description = request.POST['description','']
        brand_image = request.FILES.get('brand_image')
        brand_status = request.POST['status'] == 'on'
        
        brand = Brand.objects.create(
            brand_name = brand_name,
            description = description,
            status = brand_status
        )
        if brand_image:
            brand.brand_image = brand_image
        
        brand.save()
        return redirect('brand:brand_list')
    

class BrandStatus(View):
    def get(self, request, pk):
        brand = get_object_or_404(Brand, id=pk)
        brand.status = not brand.status
        brand.save()
        return redirect('brand:brand_list')