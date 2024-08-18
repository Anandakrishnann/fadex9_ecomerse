from django.shortcuts import render,redirect,get_object_or_404  
from django.views import View
from . models import *
from django.contrib import messages
from utils.decorators import admin_required
from django.utils.decorators import method_decorator
from utils.decorators import admin_required
from django.contrib.auth.mixins import LoginRequiredMixin
from shared.mixins import PreventBackMixin  # Import the mixin


@method_decorator(admin_required, name='dispatch')
class ProductView(PreventBackMixin,View):
    def get(self, request):
        query = request.GET.get('q')
        if query:
            products = Products.objects.filter(product_name__icontains=query)
        else:
            products = Products.objects.all()
        return render(request, 'Products/product.html', {'products':products})
    
    
@method_decorator(admin_required, name='dispatch')
class ProductCreate(PreventBackMixin,View):
    def get(self, request):
        categories = Category.objects.all()
        brands = Brand.objects.all()
        return render(request, 'Products/product_create.html', {'categories':categories, 'brands':brands})



    def post(self, request):
        product_name = request.POST.get('product_name', '').strip()
        product_description = request.POST.get('product_description', '').strip()
        product_brand_id = request.POST.get('product_brand')
        product_category_id = request.POST.get('product_category')
        price = request.POST.get('price')
        offer_price = request.POST.get('offer_price')
        status = request.POST.get('is_active') == 'on'
        thumbnail = request.FILES.get('thumbnail')

        errors = []

        
        if not product_name:
            errors.append('Product name is required.')
        
        
        if not product_description:
            errors.append('Product description is required.')

        
        try:
            price = float(price) if price else None
            offer_price = float(offer_price) if offer_price else None
        except ValueError:
            errors.append('Price and offer price must be valid numbers.')

        if price is not None and price <= 0:
            errors.append('Price must be greater than 0.')
            
        elif price > 10000000:
            errors.append('Cannot Add This Much Amount On A Product')
            
        elif price < offer_price:
            errors.append('Price Must Be Lesser Than Offer Price')
            
        
        
        if offer_price is not None and offer_price < 0:
            errors.append('Offer price cannot be negative.')
            
            
        try:
            product_brand = Brand.objects.get(id=product_brand_id) if product_brand_id else None
        except Brand.DoesNotExist:
            errors.append("Selected brand does not exist.")
            product_brand = None

        try:
            product_category = Category.objects.get(id=product_category_id) if product_category_id else None
        except Category.DoesNotExist:
            errors.append("Selected category does not exist.")
            product_category = None

        
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('product:product_create')
        
        # if not thumbnail.content_type.startswith('image/'):
        #     errors.append('Uploaded file is not an image.')

        # max_file_size = 5 * 1024 * 1024  
        # if thumbnail.size > max_file_size:
        #     errors.append('Image size should not exceed 5 MB.')

        
        product = Products.objects.create(
            product_name=product_name,
            product_description=product_description,
            product_category=product_category,
            product_brand=product_brand,
            price=price,
            offer_price=offer_price,
            is_active=status,
            thumbnail=thumbnail
        )
        product.save()

        messages.success(request, 'Product created successfully.')
        return redirect('product:product_create')
    
    

@method_decorator(admin_required, name='dispatch')
class ProductEdit(PreventBackMixin,View):
    def get(self, request, pk):
        categories = Category.objects.all()
        brands = Brand.objects.all()
        product = get_object_or_404(Products, id=pk)
        return render(request, 'Products/product_edit.html', {'product': product, 'categories': categories, 'brands': brands})
    
    def post(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        errors = []

        product_name = request.POST.get('product_name', '').strip()
        product_description = request.POST.get('product_description', '').strip()
        product_category_id = request.POST.get('product_category')
        product_brand_id = request.POST.get('product_brand')
        price = request.POST.get('price')
        offer_price = request.POST.get('offer_price')
        status = request.POST.get('is_active') == "on"
        thumbnail = request.FILES.get('thumbnail')

        if not product_name:
            errors.append('Product name is required.')

        
        if not product_description:
            errors.append('Product description is required.')

        
        try:
            price = float(price) if price else None
            offer_price = float(offer_price) if offer_price else None
            
        except ValueError:
            errors.append('Price and offer price must be valid numbers.')

        if price is not None and price <= 0:
            errors.append('Price must be greater than 0.')
            
        if offer_price is not None and offer_price < 0:
            errors.append('Offer price cannot be negative.')

        
        try:
            product_category = Category.objects.get(id=product_category_id) if product_category_id else None
        except Category.DoesNotExist:
            errors.append("Selected category does not exist.")
            product_category = None

        try:
            product_brand = Brand.objects.get(id=product_brand_id) if product_brand_id else None
        except Brand.DoesNotExist:
            errors.append("Selected brand does not exist.")
            product_brand = None

        
        if errors:
            for error in errors:
                messages.error(request, error)
            
            categories = Category.objects.all()
            brands = Brand.objects.all()
            return render(request, 'Products/product_edit.html', {'product': product, 'categories': categories, 'brands': brands})

        
        product.product_name = product_name
        product.product_description = product_description
        product.product_category = product_category
        product.product_brand = product_brand
        product.price = price
        product.offer_price = offer_price
        product.is_active = status

        if thumbnail:
            product.thumbnail = thumbnail
        
        product.save()

        messages.success(request, 'Product updated successfully.')
        return redirect('product:products')


@method_decorator(admin_required, name='dispatch')
class ProductImage(PreventBackMixin,View):
    def get(self, request, pk):
        products = get_object_or_404(Products, id=pk)
        return render(request, 'Products/product_image.html' ,{'products':products})
    
    def post(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        images = request.FILES.getlist('images')

        for image in images: 
            ProductImages.objects.create(product=product, images=image) 
        
        return redirect('product:products')


@method_decorator(admin_required, name='dispatch')
class VariantCreate(PreventBackMixin,View):
    def get(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        return render(request, 'Products/product_create_variants.html', {'product': product})
    
    def post(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        errors = []

        size = request.POST.get('size', '').strip()
        variant_stock = request.POST.get('variant_stock', '').strip()
        variant_status = request.POST.get('variant_status') == 'on'

        
        if not size:
            errors.append('Size is required.')
        
        
        try:
            variant_stock = int(variant_stock) if variant_stock else None
        except ValueError:
            errors.append('Variant stock must be a valid number.')
        
        if variant_stock is not None and variant_stock < 0:
            errors.append('Variant stock cannot be negative.')

        
        if ProductVariant.objects.filter(product=product, size=size).exists():
            errors.append('A variant with this size already exists for this product.')

        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'Products/product_create_variants.html', {'product': product})

        
        variant = ProductVariant.objects.create(
            product=product,
            size=size,
            variant_stock=variant_stock,
            variant_status=variant_status,
        )
        variant.save()

        messages.success(request, 'Product variant created successfully.')
        return redirect('product:products')



@method_decorator(admin_required, name='dispatch')
class VariantsView(PreventBackMixin,View):
    def get(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        variants = ProductVariant.objects.filter(product=product)
        return render(request, 'Products/product_variants.html', {'product':product, 'variants':variants})
    
    
    
@method_decorator(admin_required, name='dispatch')
class VariantEdit(PreventBackMixin,View):
    def get(self, request, pk):
        variant = get_object_or_404(ProductVariant, id=pk)
        return render(request, 'Products/product_edit_variant.html', {'variant': variant})
    
    def post(self, request, pk):
        variant = get_object_or_404(ProductVariant, id=pk)
        product = variant.product
        
        errors = []
        
        size = request.POST.get('size', '').strip()
        variant_stock = request.POST.get('variant_stock', '').strip()
        variant_status = request.POST.get('variant_status') == 'on'
        
        
        if not size:
            errors.append('Size is required.')
        
        
        try:
            variant_stock = int(variant_stock) if variant_stock else None
        except ValueError:
            errors.append('Variant stock must be a valid number.')
        
        if variant_stock is not None and variant_stock < 0:
            errors.append('Variant stock cannot be negative.')

        
        if ProductVariant.objects.filter(product=product, size=size).exclude(id=pk).exists():
            errors.append('A variant with this size already exists for this product.')

        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'Products/product_edit_variant.html', {'variant': variant})

        
        variant.size = size
        variant.variant_stock = variant_stock
        variant.variant_status = variant_status
        
        variant.save()
        
        messages.success(request, 'Product variant updated successfully.')
        return redirect('product:product_variant', pk=variant.product.id)

    
    
@method_decorator(admin_required, name='dispatch')
class VariantStatus(PreventBackMixin,View):
    def get(self, request, pk):
        print('VariantStatus View Called')
        
        
        variant = get_object_or_404(ProductVariant, id=pk)
        
        
        print(f'Current Variant Status: {variant.variant_status}')
        
        
        variant.variant_status = not variant.variant_status
        
        
        print(f'New Variant Status: {variant.variant_status}')
        
        
        variant.save()
        
        
        saved_variant = get_object_or_404(ProductVariant, id=pk)
        print(f'Saved Variant Status: {saved_variant.variant_status}')
        
        
        return redirect('product:product_variant', pk=variant.product.id)



@method_decorator(admin_required, name='dispatch')
class ProductStocks(PreventBackMixin,View):
    def get(self, request, pk):
        variants = ProductVariant.objects.filter(product_id=pk)
        images = ProductImages.objects.filter(product_id=pk)
        return render(request, 'Products/product_stock.html', {'variants':variants, 'images':images})



@method_decorator(admin_required, name='dispatch')
class ProductDelete(PreventBackMixin,View):
    def get(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        product.is_active = not product.is_active
        product.save()
        return redirect('product:products')



@method_decorator(admin_required, name='dispatch')
class ProductInfo(PreventBackMixin,View):
    def get(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        images = ProductImages.objects.filter(product=product) 
        variants = ProductVariant.objects.filter(product=product)
        return render(request, 'Products/product_info.html', {'product': product, 'images': images, 'variants': variants})
    


#---------------------------------------------- Review Page -------------------------------------------------------------#


class Reviews(PreventBackMixin,LoginRequiredMixin,View):
    def post(self, request, pk):
        try:
            user = Accounts.objects.get(id=request.user.id, is_active=True,is_blocked=False)
        except:
            messages.error(request,'Login to Add review')
            return redirect('accounts:login')
        
        product = get_object_or_404(Products, pk=pk)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        review = Review.objects.create(
            user = user,
            product = product,
            rating = rating,
            comment = comment
        )
        review.save()
    
        return redirect('accounts:product_details', pk=pk)
    

@method_decorator(admin_required, name='dispatch')
class DeleteImage(PreventBackMixin,View):
    def post(self, request, pk):
        image = get_object_or_404(ProductImages, id=pk)
        pk = image.product.id 
        image.delete()
        return redirect('product:product_info', pk=pk)

        
            
class DeleteReview(PreventBackMixin,View):
    def post(self, request, pk):
        review = get_object_or_404(Review, id=pk)
        try:
            if request.user == review.user:
                product_pk = review.product.id 
                review.delete()
                messages.success(request, 'Review deleted successfully.')
                return redirect('accounts:product_details', pk=product_pk)
            else:
                messages.error(request, "You cannot delete someone else's review.")
                return redirect('accounts:product_details', pk=review.product.id)
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('accounts:product_details', pk=review.product.id)
