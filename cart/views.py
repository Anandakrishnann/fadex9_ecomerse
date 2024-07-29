from django.shortcuts import get_object_or_404,redirect,render
from django.http import JsonResponse
from django.views import View
from .models import Accounts, Products, ProductVariant, Cart, CartItem
from user_panel.models import *
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from coupon.models import *


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
            
            
            available_coupons = Coupon.objects.filter(status=True, expiry_date__gte=timezone.now()) 
            used_coupons = UserCoupon.objects.filter(user=request.user).values_list('coupon', flat=True) 
            available_coupons = available_coupons.exclude(id__in=used_coupons) 
            
            return render(request, 'Cart/demo_cart.html',{'cart':cart, 'cart_item':cart_item, 'cart_total':cart_total, 'available_coupons': available_coupons })
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
        is_active = request.POST.get('is_active') == 'true' if request.POST.get('is_active') else None
        coupon_code = request.POST.get('coupon_code')
        action = request.POST.get('action')

        response = {'success': False}
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        if action == 'status' and item_id is not None and is_active is not None:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            cart_item.is_active = is_active
            cart_item.save()
            response['success'] = True
            response['message'] = 'Status updated successfully.'

        if action == 'coupon' and coupon_code:
            try:
                coupon = Coupon.objects.get(coupon_code=coupon_code)
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)
                current_total = sum(item.sub_total() for item in cart_items)
                
                if current_total > coupon.minimum_amount:
                    discount = coupon.maximum_amount
                    discount_amount = (current_total * discount / 100)

                    if discount_amount > discount:
                        discount_amount = discount
                else:
                    messages.error(request, f'Coupon only available for {coupon.minimum_amount}')
                    return redirect('cart:cart_view')
                
                new_total = current_total - discount_amount
                print(new_total)
                response.update({
                    'success': True,
                    'message': 'Coupon applied successfully.',
                    'current_total':current_total,
                    'new_total': new_total,
                    'discount': discount,
                })
                
                request.session['applied_coupon'] = coupon_code
                
            except Coupon.DoesNotExist:
                response['message'] = 'Invalid coupon code.'

        if not coupon_code:
            new_total = sum(item.sub_total() for item in cart_items)
            discount = 0
            response.update({
                'success': True,
                'new_total': new_total,
                'discount':discount
            })

        return JsonResponse(response)



class CartCheckout(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('-cart__updated_at')

        print(cart_items)
        # Check if all cart items are active and have sufficient stock
        
        if not cart_items.exists():
            messages.error(request, 'Select Product')
            return redirect('cart:cart_view')
        
        for cart_item in cart_items:
            if not cart_item.variant.variant_status:
                messages.error(request, 'variant unavailable')
                return redirect('cart:cart_view')
            
            if cart_item.variant.variant_stock < 1:
                messages.error(request, 'Out of stock')
                return redirect('cart:cart_view')
            
            if not cart_item.product.is_active:
                messages.error(request, 'Product unavailable')
                return redirect('cart:cart_view')
            
        cart_total = sum(item.sub_total() for item in cart_items)
        
        # Get applied coupon from the session (if exists)
        coupon_code = request.session.get('applied_coupon', None)
        discount = 0
        coupon_name = "Not Applied"
        if coupon_code:
            try:
                coupon = Coupon.objects.get(coupon_code=coupon_code)
                discount = coupon.maximum_amount
                coupon_name = coupon.coupon_name
                discount_amount = (cart_total * discount / 100)
                if discount_amount > discount:
                    discount_amount = discount
                cart_total -= discount_amount
            except Coupon.DoesNotExist:
                pass
            
        user_address = UserAddress.objects.filter(user=request.user.id, status=True).order_by('-status', 'id')

        return render(request, 'Cart/checkout.html', {
            'cart_items': cart_items,
            'cart_total': cart_total,
            'user_address': user_address,
            'discount':discount,
            'coupon_name':coupon_name
        })