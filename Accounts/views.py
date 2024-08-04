from datetime import timedelta
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import *
from .models import *
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import logout as auth_logout
from products.models import *
from cart.models import *
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg

#---------------------------------------------- User Side -------------------------------------------------------------#

User = get_user_model() 

# ---------------------------------------------Login View---------------------------------------------------------------
class LoginView(View):
    def get(self, request):
        # if request.user.is_authenticated:
        #     return redirect('home')
        form = EmailAuthenticationForm()
        return render(request, 'Accounts/user_side/login.html', {'form': form})

    def post(self, request):
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_active and not user.is_blocked:
                auth_login(request, user)
                messages.success(request, f"Welcome, {user.email}! You have successfully logged in.")
                return redirect('accounts:home')
            else:
                messages.error(request, 'Account is in active. Please contact support')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
        return render(request, 'Accounts/user_side/login.html', {'form': form})

#---------------------------------------------- Registration -------------------------------------------------------------#
def logout(request):
    auth_logout(request)
    return redirect('accounts:home')    


class RegisterView(View):
    
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'Accounts/user_side/register.html', {'form': form})

    def post(self, request):

        form = RegistrationForm(request.POST)

        if form.is_valid():
            user_data = form.save(commit=False)
            
            # generating otp 
            otp = get_random_string(length=6, allowed_chars='1234567890')
            print(otp)
            # otp generating time 
            otp_generation_time = timezone.now().isoformat()

            # storing the otp in the session for validate
            request.session['otp'] = otp
            request.session['otp_generation_time'] = (otp_generation_time)
            # storing the user detail's in the session for to add the data in the database
            request.session['user_data'] =  { 
                'first_name': user_data.first_name, 
                'last_name': user_data.last_name, 
                'email': user_data.email, 
                'phone_number': user_data.phone_number, 
                'password': form.cleaned_data.get('password') 
            } 
            user_data.is_active = False
            # Sending the otp through email
            send_mail(
                'Your otp code',
                f'Your OTP code is {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user_data.email],
                fail_silently=False,
            )

            messages.success(request, 'OTP has been sent to your email. Please verify to complete registration.')

            return redirect('accounts:verify-otp')
        
        return render(request, 'Accounts/user_side/register.html', {'form': form})

#---------------------------------------------- verify otp -------------------------------------------------------------#

class VerifyOtp(View):

    def get(self, request):
        form = OTPForm()
        return render(request, 'Accounts/user_side/verify_otp.html', {'form': form})

    def post(self, request):
        form = OTPForm(request.POST)

        if form.is_valid():
            otp = form.cleaned_data['otp']
            otp_generation_time_str = request.session.get('otp_generation_time')

            try:
                otp_generation_time = timezone.datetime.fromisoformat(str(otp_generation_time_str))
                current_time = timezone.now()
                otp_valid_duration = timedelta(minutes=2)

                if current_time - otp_generation_time <= otp_valid_duration:
                    if otp == request.session.get('otp'):
                        user_data = request.session.get('user_data')
                        if user_data:
                            user = Accounts.objects.create(
                                first_name=user_data.get('first_name'),
                                last_name=user_data.get('last_name'),
                                email=user_data.get('email'),
                                phone_number=user_data.get('phone_number')
                            )
                            user.set_password(user_data.get('password'))  # Set the password
                            user.is_active = True
                            user.save()

                            # Clear session data
                            del request.session['otp']
                            del request.session['otp_generation_time']
                            del request.session['user_data']

                            messages.success(request, 'Your account has been activated successfully.')
                            return redirect('accounts:login')

                        else:
                            messages.error(request, 'User data not found. Please register again.')
                    else:
                        messages.error(request, 'Invalid OTP. Please try again.')

                else:
                    messages.error(request, 'OTP has expired. Please register again.')

            except ValueError:
                messages.error(request, 'Invalid OTP generation time format.')

        return render(request, 'Accounts/user_side/verify_otp.html', {'form': form})
    
#---------------------------------------------- resend otp -------------------------------------------------------------#

class ResendOtp(View):
    
    def post(self, request):
        user_data = request.session.get('user_data') 
        print(user_data)
        if user_data: 
            otp = get_random_string(length=6, allowed_chars='1234567890') 
            otp_generation_time = timezone.now().isoformat() 
            
            request.session['otp'] = otp 
            request.session['otp_generation_time'] = otp_generation_time 
            request.session.set_expiry(120)  # OTP expires in 2 minutes 
    
            send_mail( 
                'Your OTP Code', 
                f'Your OTP code is {otp}', 
                settings.DEFAULT_FROM_EMAIL, 
                [user_data['email']], 
                fail_silently=False, 
            ) 
            
            messages.success(request, 'A new OTP has been sent to your email.') 
        else: 
            messages.error(request, 'User data not found. Please register again.') 
        return redirect('accounts:verify-otp') 
    
#---------------------------------------------- Home Page -------------------------------------------------------------#

class IndexView(View):
    def get(self, request):
        products = Products.objects.all()
        brands = Brand.objects.all()
        # return render(request, 'Accounts/user_side/home.html', {'products':products, 'brands':brands})
        return render(request, 'Accounts/user_side/home.html', {'products':products, 'brands':brands})
    

#---------------------------------------------- Product Detail Page -------------------------------------------------------------#


class ProductView(View):
    def get(self, request, pk):
        products = get_object_or_404(Products, pk=pk)
        images = ProductImages.objects.filter(product=products)
        variants = ProductVariant.objects.filter(product=products)
        reviews = Review.objects.filter(product=products)
        related_products = Products.objects.filter(product_category=products.product_category)
        return render(request, 'Accounts/user_side/product_detail.html', {
            'products': products,
            'images': images,
            'variants': variants,
            'reviews': reviews,
            'related_products':related_products,
        })


class ProductShop(View):
    def get(self, request):
        category_slug = request.GET.get('category', '')
        brand_slug = request.GET.get('brand', '')
        sort_by = request.GET.get('sort_by', '')
        search_query = request.GET.get('search', '')

        products = Products.objects.all()

        if search_query:
            products = products.filter(product_name__icontains=search_query)
        
        if category_slug:
            products = products.filter(product_category__slug=category_slug)

        if brand_slug:
            products = products.filter(product_brand__brand_name=brand_slug)

        # Annotate products with their average rating
        products = products.annotate(avg_rating=Avg('reviews__rating'))

        # Sort products based on the sort_by parameter
        if sort_by == 'price_asc':
            products = products.order_by('offer_price')
            # count = products.aggregate(count=Count(''))
        elif sort_by == 'price_desc':
            products = products.order_by('-offer_price')
        elif sort_by == 'release_date':
            products = products.order_by('-release_date')
        elif sort_by == 'avg_rating':
            products = products.order_by('-avg_rating')
        else:
            products = products.order_by('id')

        categories = Category.objects.filter(is_deleted=False)
        brands = Brand.objects.filter(status=True)
        
        
        context = {
            'products': products,
            'categories': categories,
            'brands': brands,
            'current_category': category_slug,
            'current_sort_by': sort_by,
            'search_query': search_query,
            'current_brand': brand_slug,
        }
        return render(request, 'Accounts/user_side/product_shop.html', context)

    

