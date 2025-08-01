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
from shared.mixins import PreventBackMixin  # Import the mixin
# Create your views here.


@method_decorator(admin_required, name='dispatch')
class CouponCreate(PreventBackMixin,View):
    def get(self, request):
        return render(request, 'Coupon/coupon_create.html')
    
    def post(self, request):
        coupon_name = request.POST.get('coupon_name').strip()
        minimum_amount = request.POST.get('minimum_amount')
        maximum_amount = request.POST.get('maximum_amount')
        discount = request.POST.get('discount')
        expiry_date = request.POST.get('expiry_date')
        coupon_code = request.POST.get('generated_coupon_code')  
        status = request.POST.get('status') == 'on'  
        

        errors = []

        try:
            minimum_amount = int(minimum_amount) if minimum_amount else None
            maximum_amount = int(maximum_amount) if maximum_amount else None
            discount = int(discount) if discount else None
        except ValueError:
            messages.error(request, 'Minimum Amount, Maximum Amount, and Discount must be valid numbers.')
            return redirect('coupon:create_coupon')

        errors = []
        
        if minimum_amount > 3000:
            errors.append('Minimum Amount Only Add Up To ₹3000')
        elif minimum_amount < 1000:
            errors.append('Minimum Amount Should Be Greater Than ₹1000')
        
        if maximum_amount > 8000:
            errors.append('Maximum Amount Only Add Up To ₹6000')
        elif maximum_amount < 4000:
            errors.append('Maximum Amount Should be Greater than ₹4000')

        if not coupon_name:
            errors.append('Coupon Name Required')

        if minimum_amount is None or maximum_amount is None:
            errors.append('Both Minimum and Maximum Amounts are Required')
            
            
        elif minimum_amount > maximum_amount:
            errors.append('Minimum Amount Should be Lesser than Maximum Amount')

        if discount is None:
            errors.append('Discount is Required')
            
            
        elif discount > 70:
            errors.append('Discount Can Only Be Up to 70%')

        if not expiry_date:
            errors.append('Expiry Date is Required')

        if not coupon_code:
            errors.append('Coupon Code is Required')
            
            
        elif Coupon.objects.filter(coupon_code__iexact=coupon_code).exists():
            errors.append('A Coupon with this Code Already Exists')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('coupon:create_coupon')
        
        Coupon.objects.create(
            coupon_name=coupon_name,
            minimum_amount=minimum_amount,
            maximum_amount=maximum_amount,
            discount=discount,
            expiry_date=expiry_date,
            coupon_code=coupon_code,
            status=status   
        )
        
        messages.success(request, 'Coupon Created Successfully')
        return redirect('coupon:create_coupon')
        


@method_decorator(admin_required, name='dispatch')
class EditCoupon(PreventBackMixin,View):
    def get(self, request, pk):
        coupon = get_object_or_404(Coupon, id=pk)
        return render(request, 'Coupon/edit_coupon.html', {'coupon': coupon})
    
    def post(self, request, pk):
        coupon = get_object_or_404(Coupon, id=pk)
        
        errors = []

        
        coupon_name = request.POST.get('coupon_name', '').strip()
        minimum_amount = request.POST.get('minimum_amount', '').strip()
        maximum_amount = request.POST.get('maximum_amount', '').strip()
        discount = request.POST.get('discount', '').strip()
        expiry_date = request.POST.get('expiry_date', '').strip()
        coupon_code = request.POST.get('generated_coupon_code', '').strip()
        status = request.POST.get('status') == 'on'


        try:
            minimum_amount = int(minimum_amount) if minimum_amount else None
            maximum_amount = int(maximum_amount) if maximum_amount else None
            discount = int(discount) if discount else None
        except ValueError:
            errors.append('Minimum Amount, Maximum Amount, and Discount must be valid numbers.')

        if minimum_amount is not None:
            if minimum_amount > 3000:
                errors.append('Minimum Amount Only Up To ₹3000')
            elif minimum_amount < 1000:
                errors.append('Minimum Amount Should Be Greater Than ₹1000')
        else:
            errors.append('Minimum Amount is Required')

        if maximum_amount is not None:
            if maximum_amount > 8000:
                errors.append('Maximum Amount Only Up To ₹8000')
            elif maximum_amount < 4000:
                errors.append('Maximum Amount Should Be Greater Than ₹4000')
        else:
            errors.append('Maximum Amount is Required')

        if minimum_amount is not None and maximum_amount is not None:
            if minimum_amount > maximum_amount:
                errors.append('Minimum Amount Should Be Lesser than Maximum Amount')

        if discount is not None:
            if discount > 70:
                errors.append('Discount Can Only Be Up to 70%')
        else:
            errors.append('Discount is Required')

        if not expiry_date:
            errors.append('Expiry Date is Required')

        if not coupon_code:
            errors.append('Coupon Code is Required')
        elif Coupon.objects.filter(coupon_code__iexact=coupon_code).exclude(id=pk).exists():
            errors.append('A Coupon with this Code Already Exists')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'Coupon/edit_coupon.html', {'coupon': coupon})

        # Update coupon object and save
        coupon.coupon_name = coupon_name
        coupon.minimum_amount = minimum_amount
        coupon.maximum_amount = maximum_amount
        coupon.discount = discount
        coupon.expiry_date = expiry_date
        coupon.coupon_code = coupon_code
        coupon.status = status
        coupon.save()

        messages.success(request, 'Coupon Updated Successfully')
        return redirect('coupon:coupon')




@method_decorator(admin_required, name='dispatch')
class CouponView(PreventBackMixin,View):
    def get(self, request):
        coupons = Coupon.objects.all()
        return render(request, 'Coupon/coupon.html',{'coupons':coupons})


@method_decorator(admin_required, name='dispatch')
class CouponStatus(PreventBackMixin,View):
    def post(self, request, pk):
        try:
            coupon = get_object_or_404(Coupon, id=pk)
            coupon.status = not coupon.status
            coupon.save()
            messages.success(request, 'Coupon status updated successfully.')
        except Exception as e:
            messages.error(request, f'Error updating coupon status: {e}')
        return redirect('coupon:coupon')