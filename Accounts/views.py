from datetime import timedelta
from django.shortcuts import render, redirect
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
                otp_generation_time = timezone.datetime.fromisoformat(otp_generation_time_str)
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
                            return redirect('accounts:home')

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

            return render(request, 'Accounts/user_side/home.html')
