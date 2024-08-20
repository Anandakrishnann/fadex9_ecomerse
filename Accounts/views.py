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
from django.db.models import *
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from shared.mixins import PreventBackMixin  # Import the mixin
from django.contrib.auth.forms import PasswordResetForm
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.paginator import Paginator


#---------------------------------------------- User Side -------------------------------------------------------------#

User = get_user_model() 

# ---------------------------------------------Login View---------------------------------------------------------------
class LoginView(PreventBackMixin,View):
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


class RegisterView(PreventBackMixin,View):
    
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
                    'Your OTP Code', 
                    f"""Dear {user_data.first_name},

                    Welcome to FADEX.9!

                    Thank you for joining our fashion community. We're excited to have you as a part of the FADEX.9 family, where style meets exclusivity. Our collections are carefully curated with the most unique and hyped apparel that you won't find anywhere else.

                    To complete your registration and start shopping for these exclusive pieces, please verify your email address using the One-Time Password (OTP) provided below:

                    Your OTP: "{otp}"

                    Enter this OTP on our website to verify your account and unlock access to the latest trends in men's fashion.

                    If you have any questions or need assistance, our support team is here to help. Reach out to us anytime at infofadex9@.com.

                    Stay ahead of the fashion curve!

                    Best regards,
                    The FADEX.9 Team""", 
                    settings.DEFAULT_FROM_EMAIL, 
                    [user_data.email], 
                    fail_silently=False, 
                ) 

            messages.success(request, 'OTP has been sent to your email. Please verify to complete registration.')

            return redirect('accounts:verify-otp')
        
        return render(request, 'Accounts/user_side/register.html', {'form': form})

#---------------------------------------------- verify otp -------------------------------------------------------------#

class VerifyOtp(PreventBackMixin,View):

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

class ResendOtp(PreventBackMixin,View):
    
    def post(self, request):
        user_data = request.session.get('user_data') 
        print(user_data)
        if user_data: 
            otp = get_random_string(length=6, allowed_chars='1234567890') 
            otp_generation_time = timezone.now().isoformat() 
            
            request.session['otp'] = otp 
            request.session['otp_generation_time'] = otp_generation_time 
            request.session.set_expiry(120)  # OTP expires in 2 minutes 
    
            subject = 'Your OTP Code'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [user_data.email]
            text_content = f"""
            Dear {user_data.first_name},

            Welcome to FADEX.9!

            Thank you for joining our fashion community. We're excited to have you as a part of the FADEX.9 family, where style meets exclusivity. Our collections are carefully curated with the most unique and hyped apparel that you won't find anywhere else.

            To complete your registration and start shopping for these exclusive pieces, please verify your email address using the One-Time Password (OTP) provided below:

            Your OTP: "{otp}"

            Enter this OTP on our website to verify your account and unlock access to the latest trends in men's fashion.

            If you have any questions or need assistance, our support team is here to help. Reach out to us anytime at infofadex9@.com.

            Stay ahead of the fashion curve!

            Best regards,
            The FADEX.9 Team
            """

            html_content = f"""
            <p>Dear {user_data.first_name},</p>

            <p>Welcome to FADEX.9!</p>

            <p>Thank you for joining our fashion community. We're excited to have you as a part of the FADEX.9 family, where style meets exclusivity. Our collections are carefully curated with the most unique and hyped apparel that you won't find anywhere else.</p>

            <p>To complete your registration and start shopping for these exclusive pieces, please verify your email address using the One-Time Password (OTP) provided below:</p>

            <p><strong>Your OTP: <span style="color: #ff5733;">{otp}</span></strong></p>

            <p>Enter this OTP on our website to verify your account and unlock access to the latest trends in men's fashion.</p>

            <p>If you have any questions or need assistance, our support team is here to help. Reach out to us anytime at infofadex9@.com.</p>

            <p>Stay ahead of the fashion curve!</p>

            <p>Best regards,<br>The FADEX.9 Team</p>
            """

            send_mail(
                subject=subject,
                message=text_content,
                from_email=from_email,
                recipient_list=to_email,
                fail_silently=False,
                html_message=html_content  # Use html_message to send the HTML version
            )
            
            messages.success(request, 'A new OTP has been sent to your email.') 
        else: 
            messages.error(request, 'User data not found. Please register again.') 
        return redirect('accounts:verify-otp') 
    
#---------------------------------------------- Home Page -------------------------------------------------------------#

class IndexView(PreventBackMixin,View):
    def get(self, request):
        all_products = Products.objects.all()
        products = all_products.order_by('?')[:8]
        brands = Brand.objects.all()[:6]

        return render(request, 'Accounts/user_side/home.html', {'products':products, 'brands':brands})
    

#---------------------------------------------- Product Detail Page -------------------------------------------------------------#


def get_review_percentages(product):
    total_reviews = product.reviews.count()
    if total_reviews == 0:
        return {i: 0 for i in range(1, 6)}  # return 0% for all if no reviews

    percentages = {
        5: product.reviews.filter(rating=5).count() * 100 / total_reviews,
        4: product.reviews.filter(rating=4).count() * 100 / total_reviews,
        3: product.reviews.filter(rating=3).count() * 100 / total_reviews,
        2: product.reviews.filter(rating=2).count() * 100 / total_reviews,
        1: product.reviews.filter(rating=1).count() * 100 / total_reviews,
    }
    return percentages



class ProductView(PreventBackMixin,View):
    def get(self, request, pk):
        products = get_object_or_404(Products, pk=pk)
        review_percentages = get_review_percentages(products)
        images = ProductImages.objects.filter(product=products)
        variants = ProductVariant.objects.filter(product=products)
        reviews = Review.objects.filter(product=products).order_by('-created_at')
        review_count = reviews.count()
        related_products = Products.objects.filter(product_category=products.product_category)
        return render(request, 'Accounts/user_side/product_detail.html', {
            'products': products,
            'images': images,
            'variants': variants,
            'reviews': reviews,
            'review_count':review_count,
            'related_products':related_products,
            'review_percentages':review_percentages
        })


class ProductShop(PreventBackMixin,View):
    def get(self, request):
        category_slug = request.GET.get('category', '')
        brand_slug = request.GET.get('brand', '')
        sort_by = request.GET.get('sort_by', '')
        price_range = request.GET.get('price_range', '')
        search_query = request.GET.get('search', '')

        products = Products.objects.all()

        count = 0
        
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
            
        elif sort_by == 'price_desc':
            products = products.order_by('-offer_price')
            
        elif sort_by == 'release_date':
            products = products.order_by('-release_date')
            
        elif sort_by == 'avg_rating':
            products = products.order_by('-avg_rating')
            
        else:
            products = products.order_by('id')
            

        
        if price_range == '2000-3000':
            products = products.filter(offer_price__gte=2000, offer_price__lt=3000)
            
        elif price_range == '3000-4000':
            products = products.filter(offer_price__gte=3000, offer_price__lt=4000)
            
        elif price_range == '4000-5000':
            products = products.filter(offer_price__gte=4000, offer_price__lt=5000)
            
        elif price_range == 'above_5000':
            products = products.filter(offer_price__gte=5000)
            
        elif price_range == 'all':
            products = products  # No filtering for 'all'
            
        paginator = Paginator(products, 9)  # Show 10 return requests per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        categories = Category.objects.filter(is_deleted=False)
        brands = Brand.objects.filter(status=True)
        
        count = products.aggregate(count=Count('id'))['count']
        
        context = {
            'products': page_obj,
            'categories': categories,
            'brands': brands,
            'current_category': category_slug,
            'current_sort_by': sort_by,
            'search_query': search_query,
            'current_brand': brand_slug,
            'count':count
        }
        return render(request, 'Accounts/user_side/product_shop.html', context)

    

class Contact(PreventBackMixin,View):
    def get(self, request):
        form = ContactForm(request.POST)
        return render(request, 'Accounts/user_side/contact.html',{'form':form})
    

class About(PreventBackMixin,View):
    def get(self, request):
        return render(request, 'Accounts/user_side/about.html')
    
    

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = Accounts.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "Accounts/user_side/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'FADEX.9',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email_content = render_to_string(email_template_name, c)
                    try:
                        send_mail(
                            subject,
                            email_content,
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=False,
                        )
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("accounts:password_reset_done")
    
    password_reset_form = PasswordResetForm()
    return render(request, "Accounts/user_side/password_reset.html", {"password_reset_form": password_reset_form})


def password_reset_done(request):
    return render(request, 'Accounts/user_side/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been set. You may go ahead and log in now.')
                return redirect('accounts:password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'Accounts/user_side/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The password reset link was invalid, possibly because it has already been used. Please request a new password reset.')
        return redirect('accounts:password_reset')

def password_reset_complete(request):
    return render(request, 'Accounts/user_side/password_reset_complete.html')


def contact_form(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
           # Send email
            send_mail(
                subject=f'New Contact Form Submission from {name}',
                message=(
                    f"Dear Team,\n\n"
                    f"You have received a new contact form submission on your website. Here are the details:\n\n"
                    f"Name: {name}\n"
                    f"Email: {email}\n\n"
                    f"Message:\n{message}\n\n"
                    f"Please respond to the inquiry at your earliest convenience.\n\n"
                    f"Best regards,\n"
                    f"FADEX.9"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )

            messages.success(request, 'Your message has been successfully sent, and we will get back to you as soon as possible. We appreciate your interest and look forward to assisting you.')
            return redirect('accounts:contact') 
    else:
        messages.error(request, 'There was an error sending your message. Please try again later.')
        return redirect('accounts:contact')
