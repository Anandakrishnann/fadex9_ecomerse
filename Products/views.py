from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from . models import *
from django.contrib import messages

# Create your views here.

class ProductView(View):
    def get(self, request):
        products = Products.objects.all().order_by('id')
        return render(request, 'Products/product.html', {'products':products})
    

class ProductCreate(View):
    def get(self, request):
        categories = Category.objects.all()
        brands = Brand.objects.all()
        return render(request, 'Products/product_create.html', {'categories':categories, 'brands':brands})
    
    def post(self, request):
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        product_brand_id = request.POST.get('product_brand')
        product_category_id = request.POST.get('product_category')
        price = request.POST.get('price')
        offer_price = request.POST.get('offer_price')
        status = request.POST.get('is_active') == 'on'
        
        try:
            product_brand = Brand.objects.get(id=product_brand_id) if product_brand_id else None
        except Brand.DoesNotExist:
            messages.error(request, "Selected brand does not exist.")
            return redirect('product:product_create')
        
        try:
            product_category = Category.objects.get(id=product_category_id) if product_category_id else None
        except Category.DoesNotExist:
            messages.error(request, "Selected category does not exist.")
            return redirect('product:product_create')
        
        product = Products.objects.create(
            product_name = product_name,
            product_description = product_description,
            product_category = product_category,
            product_brand = product_brand,
            price = price,
            offer_price = offer_price,
            is_active = status,
        )

        product.save()
        return redirect('product:product_create')

class ProductEdit(View):
    def get(self, request, pk):
        categories = Category.objects.all() 
        brands = Brand.objects.all() 
        product = get_object_or_404(Products, id=pk)
        return render(request, 'Products/product_edit.html', {'product': product, 'categories': categories, 'brands': brands})
    
    def post(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        product.product_name = request.POST.get('product_name')
        product.product_description = request.POST.get('product_description')
        product_category_id = request.POST.get('category')
        product_brand_id = request.POST.get('brand')
        product.price = request.POST.get('price')
        product.offer_price = request.POST.get('offer_price')
        product.is_active = request.POST.get('status') == 'on'
        
        product.product_category = Category.objects.get(id=product_category_id) if product_category_id else None 
        product.product_brand = Brand.objects.get(id=product_brand_id) if product_brand_id else None 
        
        product.save()
        
        return redirect('product:product_view')
        
class ProductImage(View):
    def get(self, request, pk):
        products = get_object_or_404(Products, id=pk)
        return render(request, 'Products/product_image.html', {'products':products})
    
    def post(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        images = request.FILES.getlist('images')
        thumbnail = request.FILES.get('thumbnail')
        
        if thumbnail:
            product.thumbnail = thumbnail
            product.save()
        
        for image in images: 
            ProductImages.objects.create(product=product, images=image) 
        
        return redirect('product:product_image', pk=pk)


class ProductVariants(View):
    def get(self, request, pk):
        product = get_object_or_404(Products, pk=pk)
        return render(request, 'Products/product_variants.html', {'product': product})
    
    def post(self, request, pk):
        product = get_object_or_404(Products, id=pk)

        size = request.POST.get('size')
        variant_stock = request.POST.get('variant_stock')
        variant_status = request.POST.get('variant_status') == 'on'

        variant = ProductVariant.objects.create(
            product=product,
            size=size,
            variant_stock=variant_stock,   
            variant_status=variant_status,
        )
        variant.save()
        
        return redirect('product:product_view')

class ProductStocks(View):
    def get(self, request, pk):
        variants = ProductVariant.objects.filter(product_id=pk)
        images = ProductImages.objects.filter(product_id=pk)
        return render(request, 'Products/product_stock.html', {'variants':variants, 'images':images})
    

class ProductDelete(View):
    def get(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        product.is_active = not product.is_active
        product.save()
        return redirect('product:product_view')

class ProductInfo(View):
    def get(self, request, pk):
        products = get_object_or_404(Products, id=pk)
        images = ProductImages.objects.filter(product=products) 
        variants = ProductVariant.objects.filter(product=products)
        return render(request, 'Products/product_info.html', {'products':products, 'images':images, 'variants':variants})