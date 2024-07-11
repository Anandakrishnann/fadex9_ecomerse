from django.shortcuts import get_object_or_404,redirect,render
from django.http import JsonResponse
from django.views import View
from .models import Accounts, Products, ProductVariant, Cart, CartItem

class AddToCart(View):
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            product_id = request.POST.get('product_id')
            variant_id = request.POST.get('variant_id')
            quantity = int(request.POST.get('quantity'))


            user = get_object_or_404(Accounts, id=user_id)
            product = get_object_or_404(Products, id=product_id)
            variant = get_object_or_404(ProductVariant, id=variant_id)

            cart, created = Cart.objects.get_or_create(user=user)

            cart_item, created = CartItem.objects.get_or_create(
                user=user,
                product=product,
                variant=variant,
                cart=cart,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return JsonResponse({'success': True, 'message': 'Product added to cart successfully!'})

        except Accounts.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User does not exist.'})

        except (Products.DoesNotExist, ProductVariant.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Product or variant does not exist.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


class CartView(View):
    def get(self,request):
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            cart_item = CartItem.objects.filter(cart=cart)
            total = total_price(request)
            return render(request, 'Cart/cart_view.html',{'cart':cart, 'cart_item':cart_item, 'total':total })
        else:
            return redirect('accounts:login')
        

class CartItemsDelete(View):
    def get(self, request, pk):
        cart_items = CartItem.objects.filter(id=pk)
        cart_items.delete()
        return redirect('cart:cart')


def total_price(request):
    total_amount = 0
    user_id = request.user
    data  = CartItem.objects.filter(user_id=user_id)
    
    for i in data:
        total_amount = i.variant.product.offer_price * i.quantity
    
    return total_amount


class UpdateCartItemQuantity(View):
    def post(self, request, *args, **kwargs):
        cart_item_id = request.POST.get('cart_item_id')
        quantity = int(request.POST.get('quantity'))

        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.quantity = quantity
        cart_item.save()

        cart = cart_item.cart
        cart_items = CartItem.objects.filter(cart=cart)
        
        total = total_price(request)
        print(total)
        
        return JsonResponse({
            'sub_total': cart_item.sub_total(),
            'total': total
        }, status = 200)