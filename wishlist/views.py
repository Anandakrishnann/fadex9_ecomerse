import json
import logging
from Accounts.models import *
from products.models import *
from cart.models import *
from user_panel.models import *
from django.http import JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from django.views import View
from django.contrib import messages
from Accounts.models import *
from orders.models import *
from shared.mixins import PreventBackMixin  # Import the mixin

# Create your views here.


class WishlistView(LoginRequiredMixin,PreventBackMixin, View):
    def get(self, request):
        try:
            user = request.user.id
            wishlists = Wishlist.objects.filter(user=user)
            return render(request, 'user_dashboard/wishlist.html', {'wishlists':wishlists})
        except:
            return render(request, 'user_dashboard/wishlist.html')
    
    


class AddToWishlist(LoginRequiredMixin, PreventBackMixin, View):
    def post(self, request):
        variant_id = request.POST.get('variant')
        if not variant_id:
            return JsonResponse({'message': 'Something went wrong'}, status=400)
        
        try:
            user = get_object_or_404(Accounts, id=request.user.id)
            variant = get_object_or_404(ProductVariant, id=variant_id)
            
            wishlist, created = Wishlist.objects.get_or_create(user=user, variant=variant)
            
            message = 'Product added to wishlist' if created else 'Product is already in your wishlist'
            return JsonResponse({'message': message}, status=200)

        except Exception as e:
            return JsonResponse({'message': f'Error: {e}'}, status=500)



class RemoveWishlist(LoginRequiredMixin,PreventBackMixin,View):
    def post(self, request, pk):
        try:
            item = get_object_or_404(Wishlist, id=pk)
            item.delete()
            return JsonResponse({'success': True, 'message': 'Product Removed Successfully'})
        except Wishlist.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})



class WishlistToCart(LoginRequiredMixin, PreventBackMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            product_id = request.POST.get('product_id')
            variant_id = request.POST.get('variant_id')
            
            print(product_id)
            print(variant_id)

            if not product_id or not variant_id:
                return JsonResponse({'success': False, 'message': 'Product or variant ID is missing.'}, status=400)

            user = get_object_or_404(Accounts, id=user_id)
            product = get_object_or_404(Products, id=product_id)
            variant = get_object_or_404(ProductVariant, id=variant_id)

            # Check if the product is active
            if not product.is_active:
                return JsonResponse({'success': False, 'message': 'Product is unavailable.'}, status=400)

            # Check stock availability
            if variant.variant_stock < 1:
                return JsonResponse({'success': False, 'message': 'Product is out of stock.'}, status=400)

            cart, created = Cart.objects.get_or_create(user=user)

            cart_item, created = CartItem.objects.get_or_create(
                product=product,
                variant=variant,
                cart=cart,
                defaults={'quantity': 1}
            )

            return JsonResponse({
                'success': True,
                'message': 'Product added to cart successfully' if created else 'Product is already in cart.'
            }, status=200)

        except (Accounts.DoesNotExist, Products.DoesNotExist, ProductVariant.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Product or variant does not exist.'}, status=400)

        except Exception as e:
            logging.error("Exception: ", exc_info=e)
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
