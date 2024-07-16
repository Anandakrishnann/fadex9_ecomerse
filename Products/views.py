from django.shortcuts import render,redirect,get_object_or_404  
from django.views import View
from . models import *
from django.contrib import messages

# Create your views here.

class ProductView(View):
    def get(self, request):
        products = Products.objects.all()
        return render(request, 'Products/product.html', {'products':products})


class ProductCreate(View):
    def get(self, request):
        if request.user.is_authenticated:
            categories = Category.objects.all()
            brands = Brand.objects.all()
            return render(request, 'Products/product_create.html', {'categories':categories, 'brands':brands})
        else:
            return render(request, 'Accounts/admin_side/admin_login.html')


    def post(self, request):
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        product_brand_id = request.POST.get('product_brand')
        product_category_id = request.POST.get('product_category')
        price = request.POST.get('price')
        offer_price = request.POST.get('offer_price')
        status = request.POST.get('is_active') == 'on'
        thumbnail = request.FILES.get('thumbnail')


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
            thumbnail = thumbnail
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
        product_category_id = request.POST.get('product_category')
        product_brand_id = request.POST.get('product_brand')
        product.price = request.POST.get('price')
        product.offer_price = request.POST.get('offer_price')
        product.is_active = request.POST.get('is_active') == 'on'
        
        product.product_category = Category.objects.get(id=product_category_id) if product_category_id else None 
        product.product_brand = Brand.objects.get(id=product_brand_id) if product_brand_id else None 
        
        product.save()
        
        return redirect('product:products')
        



        
class ProductImage(View):
    def get(self, request, pk):
        products = get_object_or_404(Products, id=pk)
        return render(request, 'Products/product_image.html' ,{'products':products})
    
    def post(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        images = request.FILES.getlist('images')

        for image in images: 
            ProductImages.objects.create(product=product, images=image) 
        
        return redirect('product:products')



class VariantCreate(View):
    def get(self, request, pk):
        product = get_object_or_404(Products, pk=pk)
        return render(request, 'Products/product_create_variants.html', {'product': product})
    
    def post(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        
        size = request.POST.get('size')
        variant_stock = request.POST.get('variant_stock')
        variant_status = request.POST.get('variant_status') == 'on'
        
        # Check if the variant with the same size already exists for the product
        if ProductVariant.objects.filter(product=product, size=size).exists():
            messages.error(request, 'A variant with this size already exists for this product.')
            return render(request, 'Products/product_create_variants.html', {'product': product})

        variant = ProductVariant.objects.create(
            product=product,
            size=size,
            variant_stock=variant_stock,   
            variant_status=variant_status,
        )
        variant.save()
        
        return redirect('product:products')
    


class VariantsView(View):
    def get(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        variants = ProductVariant.objects.filter(product=product)
        return render(request, 'Products/product_variants.html', {'product':product, 'variants':variants})


class VariantEdit(View):
    def get(self, request, pk):
        variants = ProductVariant.objects.get(id=pk)
        return render(request, 'Products/product_edit_variant.html', {'variants':variants})
    
    def post(self, request, pk):
        variant = ProductVariant.objects.get(id=pk)
        product = variant.product
        
        size = request.POST.get('size')
        variant_stock = request.POST.get('variant_stock')
        variant_status = request.POST.get('variant_status') == 'on'
        
        # Check if another variant with the new size already exists for the product
        if ProductVariant.objects.filter(product=product, size=size).exclude(id=pk).exists():
            messages.error(request, 'A variant with this size already exists for this product.')
            return render(request, 'Products/product_edit_variant.html', {'variant': variant})
        
        pk=product.id
        
        variant.size = size
        variant.variant_stock = variant_stock
        variant.variant_status = variant_status
        
        variant.save()
        
        return redirect('product:product_variant', pk=pk)
    

class VariantStatus(View):
    def get(self, request, pk):
        variant = get_object_or_404(ProductVariant, id=pk)
        pk = variant.product.id
        variant.variant_status = not variant.variant_status
        variant.save()
        return redirect('product:product_variant', pk=pk)



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
        return redirect('product:products')



class ProductInfo(View):
    def get(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        images = ProductImages.objects.filter(product=product) 
        variants = ProductVariant.objects.filter(product=product)
        return render(request, 'Products/product_info.html', {'product': product, 'images': images, 'variants': variants})
    


#---------------------------------------------- Review Page -------------------------------------------------------------#



class Reviews(View):
    def post(self, request, pk):
        user = request.user
        
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



class DeleteImage(View):
    def post(self, request, pk):
        image = get_object_or_404(ProductImages, id=pk)
        pk = image.product.id 
        image.delete()
        return redirect('product:product_info', pk=pk)



class DeleteReview(View):
    def post(self, request, pk):
        review = get_object_or_404(Review, id=pk)
        if request.user == review.user:
            print(request.user)
            print(review.user)
            pk = review.product.id 
            review.delete()
            return redirect('accounts:product_details', pk=pk)
        
            
# class DeleteReview(View):
#     def post(self, request, pk):
#         review = get_object_or_404(Review, id=pk)
#         try:
#             if request.user == review.user:
#                 print(request.user)
#                 print(review.user)
#                 pk = review.product.id 
#                 review.delete()
#                 return redirect('accounts:product_details', pk=pk)
#         except:
#             messages.error('No You Cant Delete Someones Review')
#             print(messages)
#             return redirect('accounts:product_details',{'messages':messages}, pk=pk)
        
