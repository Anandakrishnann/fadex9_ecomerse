from django.shortcuts import get_object_or_404,redirect,render
from django.http import JsonResponse
from django.views import View
from .models import *
from user_panel.models import *
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
import uuid
from django.utils.decorators import method_decorator
from utils.decorators import admin_required
# Create your views here.


@method_decorator(admin_required, name='dispatch')
class CouponCreate(View):
    def get(self, request):
        return render(request, 'Coupon/coupon_create.html')
    
    def post(self, request):
        coupon_name = request.POST.get('coupon_name')
        minimum_amount = request.POST.get('minimum_amount')
        maximum_amount = request.POST.get('maximum_amount')
        discount = request.POST.get('discount')
        expiry_date = request.POST.get('expiry_date')
        coupon_code = request.POST.get('generated_coupon_code')  # Updated to match the input ID
        status = request.POST.get('status') == 'on'  # Convert to boolean
        
    
        print(coupon_code)
        coupons = Coupon.objects.create(
            coupon_name=coupon_name,
            minimum_amount=minimum_amount,
            maximum_amount=maximum_amount,
            discount=discount,
            expiry_date=expiry_date,
            coupon_code=coupon_code,
            status=status   
        )
        
        return render(request, 'Coupon/coupon_create.html')
        

@method_decorator(admin_required, name='dispatch')
class EditCoupon(View):
    def get(self, request, pk):
        coupon = get_object_or_404(Coupon, id=pk)
        return render(request, 'Coupon/edit_coupon.html', {'coupon':coupon})
    
    def post(self, request, pk):
        coupon = get_object_or_404(Coupon, id=pk)
    
        try:
            coupon.coupon_name = request.POST['coupon_name']
            coupon.minimum_amount = request.POST['minimum_amount']
            coupon.maximum_amount = request.POST['maximum_amount']
            coupon.discount = request.POST['discount']
            coupon.expiry_date = request.POST['expiry_date']
            coupon.coupon_code = request.POST['generated_coupon_code']  # Corrected field name
            coupon.status = request.POST.get('status') == 'True'
            
            coupon.save()
            
            return redirect('coupon:coupon')
        except KeyError as e:
            error_message = f"Missing required field: {str(e)}"
            return render(request, 'Coupon/edit_coupon.html', {'coupon':coupon})
        except Exception as e:
            # Handle other exceptions
            error_message = f"An error occurred: {str(e)}"
            return render(request, 'Coupon/edit_coupon.html', {'coupon':coupon})


@method_decorator(admin_required, name='dispatch')
class CouponView(View):
    def get(self, request):
        coupons = Coupon.objects.all()
        return render(request, 'Coupon/coupon.html',{'coupons':coupons})


@method_decorator(admin_required, name='dispatch')
class CouponStatus(View):
    def post(self, request, pk):
        try:
            coupon = get_object_or_404(Coupon, id=pk)
            coupon.status = not coupon.status
            coupon.save()
            messages.success(request, 'Coupon status updated successfully.')
        except Exception as e:
            messages.error(request, f'Error updating coupon status: {e}')
        return redirect('coupon:coupon')