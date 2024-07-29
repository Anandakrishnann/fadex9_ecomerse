from datetime import datetime
import json
from django.contrib import messages
from django.shortcuts import get_object_or_404,redirect,render
from django.http import JsonResponse
from django.views import View
from .models import *
from user_panel.models import *
from products.models import *
from cart.models import *
from Accounts.models import *
from django.utils.crypto import get_random_string
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, timedelta
import razorpay
from django .conf import settings
from coupon.models import *


# Create your views here.


class OrderVerificationView(LoginRequiredMixin, View):
    def get(self, request):
        return redirect('cart:cart_checkout')
    
    def post(self, request):
        current_user = request.user
        cart = Cart.objects.get(user=current_user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        address = UserAddress.objects.get(user=current_user, order_status=True)                                      
        
        payment_option = request.POST.get('payment_option')
        
        if payment_option is None:
            messages.error(request, 'Select Payment Option')
            return redirect('cart:cart_checkout')
        
        for cart_item in cart_items:
            if not cart_item.variant.variant_status:
                messages.error(request, 'Select variant')
                return redirect('cart:cart_checkout')
            
            if cart_item.variant.variant_stock < 1:
                messages.error(request, 'Out of stock')
                return redirect('cart:cart_checkout')
            
            if not address.status:
                messages.error(request, 'Select address')
                return redirect('cart:cart_checkout')
            
            if not cart_item.product.is_active:
                messages.error(request, 'Product inactive')
                return redirect('cart:cart_checkout')
        
        current_date_time = datetime.now()
        formatted_date_time = current_date_time.strftime("%H%m%S%Y")
        unique = get_random_string(length=4, allowed_chars='1234567890')
        user = str(request.user.id)
        order_id = user+formatted_date_time+unique

        current_date_time = datetime.now()
        formatted_date_time = current_date_time.strftime("%m%Y%H%S")
        unique = get_random_string(length=2, allowed_chars='1234567890')
        user = str(request.user.id)
        payment_id = unique+user+formatted_date_time
        
        cart_items = CartItem.objects.filter(cart__user=request.user, is_active=True) 
        new_total = sum(item.sub_total() for item in cart_items) 
        
        # Get applied coupon from the session (if exists)
        coupon_code = request.session.get('applied_coupon', None)
        discount = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(coupon_code=coupon_code)
                discount = coupon.maximum_amount
                coupon_name = coupon.coupon_name
                discount_amount = (new_total * discount / 100)
                if discount_amount > discount:
                    discount_amount = discount
                new_total-= discount_amount
            except Coupon.DoesNotExist:
                pass
        
        if payment_option == "Online Payment":
            return redirect('order:online_payment')
        
        else:
            order_main = OrderMain.objects.create(
                user = current_user,
                address = address,
                total_amount = new_total,
                payment_option = payment_option,
                order_id = order_id,
                payment_id = payment_id
            )
            
            current_date_time = datetime.now()
            future_date_time = current_date_time + timedelta(days=5)
            formatted_future_date = future_date_time.strftime("Arriving By %d %a %B %Y")
            
            main_order = OrderMain.objects.get(id=order_main.id)

            
            if coupon_code:
                coupon = Coupon.objects.create(
                    user=request.user.id,
                    coupon = coupon.id,
                    used = True,
                    order = main_order
                )
            
            
            for cart_item in cart_items:
                order_sub = OrderSub.objects.create(   
                    user = current_user,  
                    main_order = main_order,
                    variant = cart_item.variant,
                    quantity = cart_item.quantity,
                )
                
                variant = cart_item.variant
                variant.variant_stock -= cart_item.quantity
                variant.save()
            
            for cart_item in cart_items:
                cart_item.delete()

            request.session.pop('applied_coupon', None)
        return render(request, 'Order/order.html', {'main_order':main_order, 'formatted_future_date':formatted_future_date})


class OnlinePayment(View):
    def get(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(cart__user=user, is_active=True) 
        new_total = sum(item.sub_total() for item in cart_items) 
        
        # Get applied coupon from the session (if exists)
        coupon_code = request.session.get('applied_coupon', None)
        discount = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(coupon_code=coupon_code)
                discount = coupon.maximum_amount
                coupon_name = coupon.coupon_name
                discount_amount = (new_total * discount / 100)
                if discount_amount > discount:
                    discount_amount = discount
                new_total-= discount_amount
            except Coupon.DoesNotExist:
                pass
            
            
        new_total_paise = int(new_total * 100)
        

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))
        payment = client.order.create({'amount': new_total_paise, 'currency': 'INR', 'payment_capture': 1})
        
        print(f"Razorpay order created: {payment}")  # Logging the payment object
        
        context = {
            'cart': new_total,
            'payment': payment,
            'razorpay_key_id': settings.RAZORPAY_KEY,
            'payment_amount': new_total_paise,
        }
        return render(request, 'Cart/razor_pay.html', context)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            print(f"Received payment data: {data}")  # Logging received data

            # Verify the payment signature
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))
            params_dict = {
                'razorpay_payment_id': data.get('razorpay_payment_id'),
                'razorpay_order_id': data.get('razorpay_order_id'),
                'razorpay_signature': data.get('razorpay_signature')
            }
            client.utility.verify_payment_signature(params_dict)

            current_user = request.user
            cart = Cart.objects.get(user=current_user)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            address = UserAddress.objects.get(user=current_user, order_status=True) 
            payment_option = "Online Payment"
            
            current_date_time = datetime.now()
            formatted_date_time = current_date_time.strftime("%H%m%S%Y")
            unique = get_random_string(length=4, allowed_chars='1234567890')
            user = str(request.user.id)
            order_id = user+formatted_date_time+unique

            payment_id = data.get('razorpay_payment_id')

            new_total = sum(item.sub_total() for item in cart_items) 
            
            coupon_code = request.session.get('applied_coupon', None)
            discount = 0
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(coupon_code=coupon_code)
                    discount = coupon.maximum_amount
                    coupon_name = coupon.coupon_name
                    discount_amount = (new_total * discount / 100)
                    if discount_amount > discount:
                        discount_amount = discount
                    new_total-= discount_amount
                except Coupon.DoesNotExist:
                    pass

            order_main = OrderMain.objects.create(
                user=current_user,
                address=address,
                total_amount=new_total,
                payment_option=payment_option,
                order_id=order_id,
                payment_id=payment_id
            )

            if coupon_code:
                coupon = Coupon.objects.create(
                    user=request.user.id,
                    coupon = coupon.id,
                    used = True,
                    order = order_main
                )
            
            for cart_item in cart_items:
                OrderSub.objects.create(
                    user=current_user,
                    main_order=order_main,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                )

                variant = cart_item.variant
                variant.variant_stock -= cart_item.quantity
                variant.save()

            cart_items.delete()
            
            request.session.pop('applied_coupon', None)

            print(f"Order created successfully: {order_main}")  # Logging order creation
            return JsonResponse({'success': True, 'message': 'Payment successful'})
        
        except json.JSONDecodeError:
            print("Invalid JSON received")
            return JsonResponse({'success': False, 'message': 'Invalid JSON'})
        
        except razorpay.errors.SignatureVerificationError as e:
            print(f"Razorpay signature verification failed: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Payment verification failed'})
        
        except Exception as e:
            print(f"Error processing payment: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
            

class OrderSuccess(View):
    def get(self, request):
        future_date_time = timezone.now() + timedelta(days=5)
        formatted_future_date = future_date_time.strftime("Arriving By %d %a %B %Y")
        
        return render(request, 'Order/order.html', {'formatted_future_date': formatted_future_date})

class AdminOrder(View):
    def get(self, request):
        orders = OrderMain.objects.all()
        return render(request, 'Order/admin_order.html', {'orders':orders})


class AdminOrderDetails(View):
    def get(self, request, pk):
        orders = OrderMain.objects.get(id=pk)
        order_sub = OrderSub.objects.filter(main_order=orders)  # Filter by main_order to get the relevant OrderSub items
        return render(request, 'Order/admin_order_details.html', {'orders': orders, 'order_sub': order_sub})
    

class CancelOrders(View):
    def post(self, request, pk):
        try:
            order = OrderMain.objects.get(id=pk)
            order_items = OrderSub.objects.filter(main_order=order)
            
            for order_item in order_items:
                order_variant = order_item.variant
                order_quantity = order_item.quantity
                
                order_variant.variant_stock += order_quantity
            
            order.order_status = "Canceled"
            order.save()
            
        except OrderMain.DoesNotExist:
            messages.error(request, 'Order does not exist.')
        return redirect('user_panel:user_dash')


class ReturnOrders(View):
    def post(self, request, pk):
        try:
            order = OrderMain.objects.get(id=pk)
            order_items = OrderSub.objects.filter(main_order=order)
            
            for order_item in order_items:
                order_variant = order_item.variant
                order_quantity = order_item.quantity
                
                order_variant.variant_stock += order_quantity
                
            order.order_status = "Returned"
            order.save()
        except:
            messages.error(request, "Order does not exist. ")
        return redirect('user_panel:user_dash')
    
    
class AdminCancelOrders(View):
    def post(self, request, pk):
        try:
            order = OrderMain.objects.get(id=pk)
            order_items = OrderSub.objects.filter(main_order=order)
            
            for order_item in order_items:
                order_variant = order_item.variant
                order_quantity = order_item.quantity
                
                order_variant.variant_stock += order_quantity
            
            order.order_status = "Canceled"
            order.save()
            
        except OrderMain.DoesNotExist:
            messages.error(request, 'Order does not exist.')
        return redirect('admin_panel:admin_orders_details')