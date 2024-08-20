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
from wallet.models import *
from django.utils.crypto import get_random_string
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, timedelta
import razorpay
from django .conf import settings
from coupon.models import *
from django.db.models import *
from decimal import Decimal
from django.utils.decorators import method_decorator
from utils.decorators import admin_required
from shared.mixins import PreventBackMixin  # Import the mixin
from django.core.paginator import Paginator

# Create your views here.


class OrderVerificationView(LoginRequiredMixin,PreventBackMixin, View):
    def get(self, request):
        return redirect('cart:cart_checkout')
    
    def post(self, request):
        current_user = request.user
        cart = Cart.objects.get(user=current_user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        try:
            address = UserAddress.objects.get(user=current_user, order_status=True,is_deleted=False)  
        except:
            messages.error(request, 'Please Select Address')
            return redirect('cart:cart_checkout')
        new_total = sum(item.sub_total() for item in cart_items)                                    
        
        payment_option = request.POST.get('payment_option')
        
        if payment_option is None:
            messages.error(request, 'Select Payment Option')
            return redirect('cart:cart_checkout')
        
        if not address:
            messages.error(request, 'Select Address To Continue')
        
        if payment_option == "Cash On Delivery" and new_total > 6000:
            messages.error(request, 'Cash On Delivery Only Available Upto 6000')
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
        
        coupon_code = request.session.get('applied_coupon', None)
        discount = 0
        
        if payment_option == "Online Payment":
            return redirect('order:online_payment')
        
        if payment_option == "Wallet" :
                current_user = request.user
                try:
                    wallet = Wallet.objects.get(user=current_user)
                    wallet_amount = wallet.balance
                    
                    cart_items = CartItem.objects.filter(cart__user=request.user, is_active=True)
                    new_total = sum(item.sub_total() for item in cart_items)
                    
                    if new_total <= wallet_amount:
                        wallet = Wallet.objects.get(user=current_user)
                        address = UserAddress.objects.get(user=current_user, order_status=True)
                        payment_option = "Wallet Payment"
                        
                        current_date_time = datetime.now()
                        formatted_date_time = current_date_time.strftime("%H%m%S%Y")
                        unique = get_random_string(length=4, allowed_chars='1234567890')
                        user = str(request.user.id)
                        order_id = user + formatted_date_time + unique
                        
                        formatted_date_time = current_date_time.strftime("%m%Y%H%S")
                        unique = get_random_string(length=2, allowed_chars='1234567890')
                        payment_id = unique + user + formatted_date_time

                        coupon_code = request.session.get('applied_coupon', None)
                        discount = 0
                        final_amount = new_total
                        discount_amount = 0
                        
                        if coupon_code:
                            try:
                                coupon = Coupon.objects.get(coupon_code=coupon_code)
                                discount = coupon.maximum_amount
                                discount_amount = (new_total * discount / 100)
                                if discount_amount > discount:
                                    discount_amount = discount
                                final_amount -= discount_amount
                            except Coupon.DoesNotExist:
                                pass
                                    
                        order_address = OrderAddress.objects.create(
                            name=address.name,
                            house_name=address.house_name,
                            street_name=address.street_name,
                            pin_number=address.pin_number,
                            district=address.district,
                            state=address.state,
                            country=address.country,
                            phone_number=address.phone_number
                        )
                        
                        order_status = "Confirmed"
                        
                        order_main = OrderMain.objects.create(
                            user=current_user,
                            address=order_address,
                            total_amount=new_total,
                            final_amount=final_amount,
                            discount_amount=discount_amount,
                            payment_option=payment_option,
                            order_id=order_id,
                            order_status=order_status,
                            payment_id=payment_id,
                            payment_status=True
                        )

                        for cart_item in cart_items:
                            OrderSub.objects.create(
                                user=current_user,
                                main_order=order_main,
                                variant=cart_item.variant,
                                price=cart_item.product.offer_price,
                                quantity=cart_item.quantity,
                            )

                            cart_item.variant.variant_stock -= cart_item.quantity
                            cart_item.variant.save()
                            
                        order_amount = new_total
                        description = "Product Purchased With Wallet"
                        transaction_type = "Debited"
                        
                        transaction = Transaction.objects.create(
                            wallet=wallet,
                            description=description,
                            amount=order_amount,
                            transaction_type=transaction_type,
                        )

                        wallet.balance -= final_amount 
                        wallet.save()
                        
                        cart_items.delete()
                        
                        request.session['order_id'] = order_main.order_id
                        request.session['order_date'] = order_main.date.strftime("%Y-%m-%d")
                        request.session['order_status'] = order_main.order_status
                        
                        request.session.pop('applied_coupon', None)
                        
                        messages.success(request, 'Order Success')
                        
                        return redirect('order:order_success')
                    else:
                        messages.error(request, 'Not Enough Money In Wallet')
                        return redirect('cart:cart_checkout')
                except Wallet.DoesNotExist:
                    messages.error(request, 'Wallet Does Not Exist')
                    return redirect('cart:cart_checkout')
                except Exception as e:
                    messages.error(request, str(e))
                    return redirect('cart:cart_checkout')
        else:
            
            user = request.user
            cart_items = CartItem.objects.filter(cart__user=user, is_active=True) 
            new_total = sum(item.sub_total() for item in cart_items) 
            
            current_date_time = datetime.now()
            formatted_date_time = current_date_time.strftime("%H%m%S%Y")
            unique = get_random_string(length=4, allowed_chars='1234567890')
            user = str(request.user.id)
            order_id = user + formatted_date_time + unique
            
            formatted_date_time = current_date_time.strftime("%m%Y%H%S")
            unique = get_random_string(length=2, allowed_chars='1234567890')
            payment_id = unique + user + formatted_date_time

            coupon_code = request.session.get('applied_coupon', None)
            discount = 0
            final_amount = new_total
            discount_amount = 0
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(coupon_code=coupon_code)
                    discount = coupon.maximum_amount
                    discount_amount = (new_total * discount / 100)
                    if discount_amount > discount:
                        discount_amount = discount
                    final_amount -= discount_amount
                except Coupon.DoesNotExist:
                    pass
            
            order_address = OrderAddress.objects.create(
                name=address.name,
                house_name=address.house_name,
                street_name=address.street_name,
                pin_number=address.pin_number,
                district=address.district,
                state=address.state,
                country=address.country,
                phone_number=address.phone_number
            )
            
            order_status = "Confirmed"
            
            order_main = OrderMain.objects.create(
                user=current_user,
                address=order_address,
                total_amount=new_total,
                final_amount=final_amount,
                discount_amount=discount_amount,
                payment_option=payment_option,
                order_id=order_id,
                order_status=order_status,
                payment_id=payment_id,
                payment_status=False
            )
            
            

            for cart_item in cart_items:
                OrderSub.objects.create(
                    user=current_user,
                    main_order=order_main,
                    variant=cart_item.variant,
                    price=cart_item.product.offer_price,
                    quantity=cart_item.quantity,
                )

                cart_item.variant.variant_stock -= cart_item.quantity
                cart_item.variant.save()

            cart_items.delete()

            request.session['order_id']=order_main.order_id
            request.session['order_date'] = order_main.date.strftime("%Y-%m-%d")
            request.session['order_status']=order_main.order_status
            
            request.session.pop('applied_coupon', None)
            
            messages.success(request, 'Order Success')
            
            return redirect('order:order_success')



class OnlinePayment(LoginRequiredMixin,PreventBackMixin,View):
    def get(self, request):
        try:
            user = request.user
            cart_items = CartItem.objects.filter(cart__user=user, is_active=True) 
            new_total = sum(item.sub_total() for item in cart_items) 
            
            coupon_code = request.session.get('applied_coupon', None)
            discount = 0
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(coupon_code=coupon_code)
                    if new_total >= coupon.minimum_amount:
                        discount = coupon.discount
                        discount_amount = (new_total * discount / 100)
                        discount_amount = min(discount_amount, coupon.maximum_amount)
                        
                        new_total = new_total - discount_amount
                        request.session['applied_coupon'] = coupon_code
                    else:
                        messages.error(request, f'Coupon only available for orders over {coupon.minimum_amount}')
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
        except:
            messages.error(request, 'No Internet Connection')
            return redirect('cart:cart_checkout')
        
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
            address = UserAddress.objects.get(user=current_user, order_status=True,is_deleted=False)
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
            final_amount = new_total
            discount_amount = 0
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(coupon_code=coupon_code)
                    discount = coupon.maximum_amount
                    coupon_name = coupon.coupon_name
                    discount_amount = (new_total * discount / 100)
                    if discount_amount > discount:
                        discount_amount = discount
                    final_amount-= discount_amount
                except Coupon.DoesNotExist:
                    pass
                
            order_address = OrderAddress.objects.create(
                name = address.name,
                house_name = address.house_name,
                street_name = address.street_name,
                pin_number = address.pin_number,
                district = address.district,
                state = address.state,
                country = address.country,
                phone_number = address.phone_number
            )
            
            order_address = OrderAddress.objects.get(id=order_address.id)
            
            order_status = "Shipped"
            
            order_main = OrderMain.objects.create(
                user=current_user,
                address=order_address,
                total_amount=new_total,
                discount_amount=discount_amount,
                final_amount=final_amount,
                payment_option=payment_option,
                order_id=order_id,
                order_status = order_status,
                payment_id=payment_id,
                payment_status = True
            )

            main_order = OrderMain.objects.get(id=order_main.id)

            if coupon_code:
                coupon = Coupon.objects.get(coupon_code=coupon_code)
                coupon = UserCoupon.objects.create(
                    user=request.user,
                    coupon = coupon,
                    used = True,
                    order = main_order
                )
            
            for cart_item in cart_items:
                OrderSub.objects.create(
                    user=current_user,
                    main_order=order_main,
                    variant=cart_item.variant,
                    price=cart_item.product.offer_price,
                    quantity=cart_item.quantity,
                )

                variant = cart_item.variant
                variant.variant_stock -= cart_item.quantity
                variant.save()
            
            cart_items.delete()
            
            request.session['order_id']=order_main.order_id
            request.session['order_date'] = order_main.date.strftime("%Y-%m-%d")
            request.session['order_status']=order_main.order_status
            
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



class OrderSuccess(LoginRequiredMixin,PreventBackMixin,View):
    def get(self, request):
        future_date_time = timezone.now() + timedelta(days=5)
        formatted_future_date = future_date_time.strftime("Arriving By %d %a %B %Y")
        order_id = request.session.get('order_id', None)
        date = request.session.get('order_date', None)
        order_status = request.session.get('order_status', None)
        
        return render(request, 'Order/order.html', {'formatted_future_date': formatted_future_date, 'order_id':order_id, 'date':date, 'order_status':order_status})



@method_decorator(admin_required, name='dispatch')
class AdminOrder(PreventBackMixin, View):
    def get(self, request):
        search_query = request.GET.get('search', '').strip()
        status_filter = request.GET.get('status', '').strip()

        orders = OrderMain.objects.all().order_by('-updated_at')

        if search_query:
            orders = orders.filter(order_id__icontains=search_query)

        if status_filter and status_filter != 'Show all':
            if status_filter == 'Active':
                orders = orders.filter(is_active=True)
            elif status_filter == 'Inactive':
                orders = orders.filter(is_active=False)

        # Pagination
        paginator = Paginator(orders, 5)  # Show 10 orders per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'Order/admin_order.html', {
            'orders': page_obj,
            'search_query': search_query,
            'status_filter': status_filter,
        })




@method_decorator(admin_required, name='dispatch')
class AdminOrderDetails(PreventBackMixin,View):
    def get(self, request, pk):
        orders = OrderMain.objects.get(id=pk)
        order_sub = OrderSub.objects.filter(main_order=orders)  # Filter by main_order to get the relevant OrderSub items
        return render(request, 'Order/admin_order_details.html', {'orders': orders, 'order_sub': order_sub})


class CancelOrders(LoginRequiredMixin,PreventBackMixin,View):
    def post(self, request, pk):
        try:
            order = OrderMain.objects.get(id=pk)
            order_items = OrderSub.objects.filter(main_order=order,is_active=True)
            
            if not order.is_active: 
                messages.error(request, 'Order item is already Canceled.') 
                return redirect('user_panel:user_dash')
            
            for order_item in order_items:
                order_variant = order_item.variant
                order_quantity = order_item.quantity
                
                order_variant.variant_stock += order_quantity

            
            order.order_status = "Canceled"
            order.is_active = False
            order.save()
            
            if order.payment_option == "Online Payment" or order.payment_option == "Wallet Payment":
                
                item_refund = 0
                
                for item in order_items:
                    item_amount = Decimal(str(item.price * item.quantity))
                    order_amount = Decimal(str(order.total_amount))
                    order_discount_amount = Decimal(str(order.discount_amount))
                    
                    item_discount_amount =  (order_discount_amount * item_amount) / order_amount
                    item_refund_amount = item_amount - item_discount_amount

                    item_refund += item_refund_amount
                    item.is_active = False
                    item.main_order.final_amount -= item_refund
                    item.save()
                
                if item_refund >= 0:
                    description = f"Refund for Cancel order {order.order_id}"
                    transaction_type = "Credited"
                    
                    wallet, created = Wallet.objects.get_or_create(user=request.user)
                    
                    transaction = Transaction.objects.create(
                    wallet = wallet,
                    description=description,
                    amount=item_refund,
                    transaction_type=transaction_type,
                    )
                    
                    wallet.balance += Decimal(item_refund)  # Ensure Decimal type for accurate calculation
                    wallet.save()
                    
                order.final_amount -= item_refund
                order.save()
            
        except OrderMain.DoesNotExist:
            messages.error(request, 'Order does not exist.')
            return redirect('user_panel:user_dash')
        
        return redirect('user_panel:user_dash')


class ReturnOrders(LoginRequiredMixin,PreventBackMixin, View):
    def post(self, request, pk):
        try:
            order = OrderMain.objects.get(id=pk)
            order_items = OrderSub.objects.filter(main_order=order)
            
            if not order.is_active: 
                messages.error(request, 'Order item is already returned.') 
                return redirect('user_panel:user_dash')
            
            if order.order_status in ['Pending', 'Confirmed', 'Shipped']: 
                messages.error(request, 'Order cannot be returned at this stage.') 
                return redirect('user_panel:user_dash') 
            
            reason = request.POST.get('reason', '').strip()
            if not reason:
                messages.error(request, 'A reason must be provided for returns.')
                return redirect('user_panel:user_dash')
            
            ReturnRequest.objects.create(
                order_main=order,
                reason=reason
            )
            
            order.order_status = "Pending" 
            order.save()
            
            messages.success(request, "Please wait for the admin's approval.")
            return redirect('user_panel:user_dash')
        
        except OrderMain.DoesNotExist:
            messages.error(request, "Order does not exist.")
        
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
        
        return redirect('user_panel:user_dash')



@method_decorator(admin_required, name='dispatch')
class AdminCancelOrders(PreventBackMixin,View):
    def post(self, request, pk):
        try:
            order = OrderMain.objects.get(id=pk)
            order_items = OrderSub.objects.filter(main_order=order,is_active=True)
            
            for order_item in order_items:
                order_variant = order_item.variant
                order_quantity = order_item.quantity
                
                order_variant.variant_stock += order_quantity
            
            order.order_status = "Canceled"
            order.save()
            
            refund_amount = Decimal('0.00') 
            
            if order.payment_option == "Online Payment" or order.payment_option == "Wallet Payment": 
                
                for item in order_items: 
                    item_total_cost = Decimal(str(item.final_total_cost())) 
                    order_total_amount = Decimal(str(item.main_order.total_amount)) 
                    order_discount_amount = Decimal(str(item.main_order.discount_amount)) 

                    item_discount_amount = (order_discount_amount * item_total_cost) / order_total_amount 
                    item_refund_amount = item_total_cost - item_discount_amount 

                    refund_amount += item_refund_amount 
                    order.is_active = False 
                    order.save() 
                
                if refund_amount > 0:
                    description = f"Sorry Due To Some Reason Admin Canceled This Order {order.order_id}"
                    transaction_type = "Credited"
                    
                    wallet, created = Wallet.objects.get_or_create(user=order.user)
                    
                    transaction, created = Transaction.objects.get_or_create(
                    wallet = wallet,
                    description=description,
                    amount=refund_amount,
                    transaction_type=transaction_type,
                    )
                    
                    wallet.balance += Decimal(refund_amount)
                    wallet.save()
                    
                order.final_amount -= refund_amount
                order.save()
                
                messages.success(request, 'Order Canceled credited to the user\'s wallet.') 
                return redirect('order:admin_orders_details',pk=order.id)
                
            else:
                messages.success(request, 'Order Canceled Successfully')
                return redirect('order:admin_orders_details',pk=order.id)

        except OrderMain.DoesNotExist:
            messages.error(request, 'Order does not exist.')
        return redirect('admin_panel:admin_orders_details',pk=order.id)
    

@method_decorator(admin_required, name='dispatch')
class AdminReturnRequests(PreventBackMixin, View):
    def get(self, request):
        search_query = request.GET.get('search', '').strip()

        if search_query:
            return_requests = ReturnRequest.objects.filter(order_main__order_id__icontains=search_query).order_by('-created_at')
        else:
            return_requests = ReturnRequest.objects.all().order_by('-created_at')

        # Pagination
        paginator = Paginator(return_requests, 5)  # Show 10 return requests per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'Order/return_request.html', {
            'return_requests': page_obj,
            'search_query': search_query,
        })

@method_decorator(admin_required, name='dispatch')
class AdminReturnApproval(PreventBackMixin,View):
    def post(self, request, pk):
        return_request = get_object_or_404(ReturnRequest, id=pk) 
        action = request.POST.get('action')
        
        if action == 'Approve':
            return_request.status = "Approved"
            return_request.save()
            
            refund_amount = Decimal('0.00') 
            
            if return_request.order_sub:  

                item = return_request.order_sub 
                main_order = item.main_order 
                item_total_cost = Decimal(str(item.final_total_cost()))
                order_total_amount = Decimal(str(main_order.total_amount)) 
                order_discount_amount = Decimal(str(main_order.discount_amount)) 
                
                item_discount_amount = (order_discount_amount * item_total_cost) / order_total_amount 
                refund_amount = item_total_cost - item_discount_amount 
                
                item.is_active = False 
                item.status = "Returned"
                item.save() 
                
                order = return_request.order_main
                order.final_amount -= refund_amount
                order.save()
                
                all_canceled = not main_order.ordersub_set.filter(is_active=True).exists() 
                
                if all_canceled: 

                    main_order.order_status = 'Returned' 
                    main_order.save() 
                    
            else:

                order = return_request.order_main 
                active_items = order.ordersub_set.filter(is_active=True) 
                
                for item in active_items: 
                    item_total_cost = Decimal(str(item.final_total_cost())) 
                    order_total_amount = Decimal(str(order.total_amount)) 
                    order_discount_amount = Decimal(str(order.discount_amount)) 

                    item_discount_amount = (order_discount_amount * item_total_cost) / order_total_amount 
                    item_refund_amount = item_total_cost - item_discount_amount 

                    refund_amount += item_refund_amount 
                    item.is_active = False 
                    item.status = "Returned"
                    item.save() 

                order.order_status = 'Returned' 
                order.is_active = False 
                order.final_amount -= refund_amount
                order.save()

            if refund_amount > 0 and return_request.order_main.payment_status: 
                    wallet, created = Wallet.objects.get_or_create(user=return_request.order_main.user) 

                    wallet.balance += refund_amount 
                    wallet.updated_at = timezone.now() 
                    wallet.save() 
                    
                    Transaction.objects.create( 
                        wallet=wallet, 
                        amount=float(refund_amount), 
                        description=f"Refund for {'order' if return_request.order_sub is None else 'item'} {return_request.order_main.order_id if return_request.order_sub is None else return_request.order_sub.variant.product.product_name}", 
                        transaction_type='Credited' 
                    )
                    
                    messages.success(request, 'Return request approved and amount credited to the user\'s wallet.') 
                    return redirect('order:return_requests')
            else: 
                messages.success(request, 'Return request approved. No payment was made or payment status is not confirmed.') 
                return redirect('order:return_requests')
            
        elif action == "Reject": 
            return_request.status = "Rejected" 
            return_request.order_sub.status = "Return Rejected"
            return_request.save() 
            messages.success(request, 'Return request rejected.') 
            return redirect('order:return_requests')
        
        else:
            messages.error(request, 'Invalid action.')
            return redirect('order:return_requests')




class IndividualCancel(LoginRequiredMixin,PreventBackMixin,View):
    def post(self, request, pk):
        order_sub = get_object_or_404(OrderSub, id=pk, user=request.user)

        if not order_sub.is_active: 
            messages.error(request, 'Order item is already canceled.') 
            return redirect('user_panel:user_dash') 

        if order_sub.main_order.order_status not in ['Pending', 'Confirmed', 'Shipped', 'Order Placed']: 
            messages.error(request, 'Order cannot be canceled at this stage.') 
            return redirect('user_panel:user_dash') 

        if order_sub.main_order.payment_option in ['Online Payment', 'Wallet Payment']: 

            item_total_cost = Decimal(order_sub.total_cost()) 
            order_total_amount = Decimal(order_sub.main_order.total_amount) 
            order_discount_amount = Decimal(order_sub.main_order.discount_amount) 

            item_discount_amount = (order_discount_amount * item_total_cost) / order_total_amount 
            refund_amount = item_total_cost - item_discount_amount 

            wallet, created = Wallet.objects.get_or_create(user=request.user) 
            
            wallet.balance += refund_amount
            wallet.updated_at = timezone.now() 
            wallet.save() 

            Transaction.objects.create( 
                wallet=wallet, 
                amount=float(refund_amount), 
                description=f'Refund for canceled item {order_sub.variant.product.product_name}', 
                transaction_type='Credited' 
            ) 

        order_sub.is_active = False 
        order_sub.main_order.final_amount -= refund_amount
        order_sub.save() 

        all_canceled = not order_sub.main_order.ordersub_set.filter(is_active=True).exists() 

        if all_canceled: 
            order_sub.main_order.order_status = 'Canceled' 
            order_sub.main_order.save() 

        order_sub.variant.variant_stock += order_sub.quantity
        order_sub.status="Canceled"
        order_sub.variant.save()

        messages.success(request, 'Order item canceled successfully.') 
        return redirect('user_panel:user_dash')


class IndividualReturn(PreventBackMixin,View):
    def post(self, request, pk):
        order_sub = get_object_or_404(OrderSub, id=pk, user=request.user)

        if not order_sub.is_active: 
            messages.error(request, 'Order item is already Returned.') 
            return redirect('user_panel:user_dash') 

        if order_sub.main_order.order_status in ['Pending', 'Confirmed', 'Shipped', 'Canceled']: 
            messages.error(request, 'Order cannot be Return at this stage.') 
            return redirect('user_panel:user_dash') 

        reason = request.POST.get('reason', '').strip()

        if not reason:
            messages.error(request, 'A reason must be provided for returns.')
            return redirect('user_panel:user_dash')

        ReturnRequest.objects.create(
            order_main = order_sub.main_order,
            order_sub = order_sub,
            reason = reason
        )

        order_sub.status = "Return Requested"
        order_sub.save()

        messages.success(request, "Please wait for the admin's approval.") 
        return redirect('user_panel:user_dash')