from django.shortcuts import get_object_or_404,redirect,render
from django.http import JsonResponse
from django.views import View
from .models import Accounts, Products, ProductVariant, Cart, CartItem
from user_panel.models import *
import logging
from django.contrib.auth.mixins import LoginRequiredMixin


class AddToCart(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            product_id = request.POST.get('product_id')
            variant_id = request.POST.get('variant_id')

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
                quantity=1  
            )
            return JsonResponse({'success': True, 'message': 'Product added to cart successfully'}, status=200)

        except Accounts.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User does not exist.'}, status=400)

        except (Products.DoesNotExist, ProductVariant.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Product or variant does not exist.'}, status=400)

        except Exception as e:
            logging.error("Exception: ", exc_info=e)
            return JsonResponse({'success': False, 'message': str(e)}, status=500)



class CartView(LoginRequiredMixin, View):
    def get(self,request):
        try:
            cart = get_object_or_404(Cart, user=request.user)
            cart_item = CartItem.objects.filter(cart=cart).order_by('-cart__updated_at')
            cart_prices = CartItem.objects.filter(cart=cart, is_active=True)
            cart_total = sum(item.sub_total() for item in cart_prices)
            
            return render(request, 'Cart/demo_cart.html',{'cart':cart, 'cart_item':cart_item, 'cart_total':cart_total})
        except:
            return render(request, 'Cart/demo_cart.html')




class CartItemsDelete(LoginRequiredMixin, View):
    def get(self, request, pk):
        cart_items = CartItem.objects.filter(id=pk)
        cart_items.delete()
        return redirect('cart:cart_view')



def update_cart_quantity(request): 
    if request.method == 'POST': 
        item_id = request.POST.get('item_id') 
        new_quantity = int(request.POST.get('quantity')) 

        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user) 
        cart_item.quantity = new_quantity 
        cart_item.save() 

        cart_items = CartItem.objects.filter(cart__user=request.user, is_active=True) 
        new_total = sum(item.sub_total() for item in cart_items) 
        item_sub_total = cart_item.sub_total() 

        return JsonResponse({ 
            'success': True, 
            'new_total': new_total, 
            'item_sub_total': item_sub_total, 
        }) 

    return JsonResponse({'success': False})


class UpdateCartStatus(View):
    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        is_active = request.POST.get('is_active') == 'true'  # corrected the logic here

        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.is_active = is_active
        cart_item.save()

        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        new_total = sum(item.sub_total() for item in cart_items)  # Make sure you have a sub_total method

        return JsonResponse({
            'success': True,
            'new_total': new_total,
        })


class CartCheckout(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('-cart__updated_at')

        
        # Check if all cart items are active and have sufficient stock
        for cart_item in cart_items:
            if not cart_item.variant.variant_status or cart_item.variant.variant_stock < 1 or not cart_item.product.is_active or cart_item.variant.variant_stock < cart_item.quantity:
                return redirect('cart:cart_view')  # Redirect to cart page if any item is not active or out of stock

        cart_total = sum(item.sub_total() for item in cart_items)
        user_address = UserAddress.objects.filter(user=request.user.id, status=True).order_by('-status', 'id')

        return render(request, 'Cart/checkout.html', {
            'cart_items': cart_items,
            'cart_total': cart_total,
            'user_address': user_address,
        })