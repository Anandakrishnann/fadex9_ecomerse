from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from django.views import View
from django.contrib import messages
from Accounts.models import *
from orders.models import *
from django.contrib.auth import authenticate, login
from wallet.models import *
from django.db.models import *
from django.http import HttpResponse

# Create your views here.



#---------------------------------------------- User Address Page -------------------------------------------------------------#


class UserDashboard(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        user_data = Accounts.objects.get(email=user.email)
        user_address = UserAddress.objects.filter(user=user, is_deleted=False).order_by('-updated_at')
        orders = OrderMain.objects.filter(user=request.user.id).order_by('-updated_at')
        order_sub = OrderSub.objects.filter(user=request.user.id)
        
        balance = 0  # Initialize balance to 0 by default
        wallets = None  # Initialize wallets to None by default
        try:
            wallets = Wallet.objects.get(user=user)
            balance = wallets.balance
        except Wallet.DoesNotExist:
            pass
        
        transactions = Transaction.objects.filter(wallet=wallets)
        
        return render(request, 'user_dashboard/user_dash.html', {
            'user_address': user_address,
            'user_data': user_data,
            'user': user,
            'orders': orders,
            'order_sub': order_sub,
            'balance': balance,
            'transactions':transactions
        })



class UserDetails(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        try:
            user_details = get_object_or_404(Accounts, email=user)
            return render(request, 'user_dashboard/user_details.html', {'user_details':user_details})
        except:
            return redirect('accounts:login')



class EditDetails(LoginRequiredMixin, View):
    def get(self, request, pk):
        user = Accounts.objects.get(id=pk)
        return render(request, 'user_dashboard/user_dash.html', {'user':user})
    
    def post(self, request, pk):
        user = Accounts.objects.get(id=pk)
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        email = request.POST.get('email').strip()
        phone_number = request.POST.get('phone_number').strip()
        
        if not first_name or not last_name:
            messages.error(request, "First name and last name cannot be empty.")
            return render(request, 'user_dashboard/user_dash.html', {'user': user})

        if Accounts.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "This email is already in use.")
            return render(request, 'user_dashboard/user_dash.html', {'user': user})

        if len(phone_number) != 10 or not phone_number.isdigit():
            messages.error(request, "Phone number must be 10 digits and contain only numbers.")
            return render(request, 'user_dashboard/user_dash.html', {'user': user})

        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        user.save()
        messages.success(request, 'Address Edited Successfully')
        return redirect('user_panel:user_dash')



class ChangePassword(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_dashboard/user_dash.html')
    
    def post(self, request):
        user = self.request.user

        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if user.check_password(old_password):  
            if new_password == confirm_new_password and new_password != old_password:
                user.set_password(new_password) 
                user.save()
                messages.success(request, 'Password Changed Successfully')
                
                user = authenticate(username=request.user, password=new_password)
                if user is not None:
                    login(request, user)
                else:
                    messages.error(request, 'Authentication failed. Please login again.')
                    
                return redirect('user_panel:change_password')
            else:
                messages.error(request, 'New Passwords Do Not Match or Same as Old')
        else:
            messages.error(request, 'Old Password Incorrect')

        return render(request, 'user_dashboard/user_dash.html')



class CreateAddress(LoginRequiredMixin, View):
    def post(self, request):
        users = request.user
        name = request.POST.get('name').strip()
        house_name = request.POST.get('house_name').strip()
        street_name = request.POST.get('street_name').strip()
        pin_number = request.POST.get('pin_number').strip()
        district = request.POST.get('district').strip()
        state = request.POST.get('state').strip()
        country = request.POST.get('country').strip()
        phone_number = request.POST.get('phone_number').strip()
        status = request.POST.get('status') == "on"

        
        if not name or not house_name or not street_name or not pin_number or not district or not state or not country or not phone_number:
            messages.error(request, "All fields are required.")
            return redirect('user_panel:user_dash')
        
        
        if not pin_number.isdigit() or len(pin_number) != 6:
            messages.error(request, "Please enter a valid 6-digit PIN number.")
            return redirect('user_panel:user_dash')

        
        if not phone_number.isdigit() or len(phone_number) not in [10, 12]:
            messages.error(request, "Please enter a valid phone number with 10 or 12 digits.")
            return redirect('user_panel:user_dash')

        
        address = UserAddress.objects.create(
            user=users,
            name=name,
            house_name=house_name,
            street_name=street_name,
            pin_number=pin_number,
            district=district,
            state=state,
            country=country,
            phone_number=phone_number,
            status=status,
        )
        
        address.save()
        return redirect('user_panel:user_dash')



class EditAddress(LoginRequiredMixin, View):
    def get(self, request, pk):
        users = get_object_or_404(UserAddress, id=pk)
        return render(request, 'user_dashboard/edit_address.html', {'users':users})
    
    def post(self, request, pk):
        users = get_object_or_404(UserAddress, id=pk)
        
        users.user = request.user
        name = request.POST.get('name').strip()
        house_name = request.POST.get('house_name').strip()
        street_name = request.POST.get('street_name').strip()
        pin_number = request.POST.get('pin_number').strip()
        district = request.POST.get('district').strip()
        state = request.POST.get('state').strip()
        country = request.POST.get('country').strip()
        phone_number = request.POST.get('phone_number').strip()
        status = request.POST.get('status') == "on"

        # Validate required fields
        if not name or not house_name or not street_name or not pin_number or not district or not state or not country or not phone_number:
            messages.error(request, "All fields are required.")
            return redirect('user_panel:user_dash')

        # Validate pin number
        if not pin_number.isdigit() or len(pin_number) != 6:
            messages.error(request, "Please enter a valid 6-digit PIN number.")
            return redirect('user_panel:user_dash')

        # Validate phone number
        if not phone_number.isdigit() or len(phone_number) not in [10, 12]:
            messages.error(request, "Please enter a valid phone number with 10 or 12 digits.")
            return redirect('user_panel:user_dash')

        # Update the user address
        users.name = name
        users.house_name = house_name
        users.street_name = street_name
        users.pin_number = pin_number
        users.district = district
        users.state = state
        users.country = country
        users.phone_number = phone_number

        # Handle the status update
        if users.status:
            UserAddress.objects.filter(user=users.user).update(status=False)
        users.status = status
        
        users.save()

        return redirect('user_panel:user_dash')


class AddAddress(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_dashboard/add_new_address.html' )
    
    def post(self, request):
        users = request.user
        name = request.POST.get('name').strip()
        house_name = request.POST.get('house_name').strip()
        street_name = request.POST.get('street_name').strip()
        pin_number = request.POST.get('pin_number').strip()
        district = request.POST.get('district').strip()
        state = request.POST.get('state').strip()
        country = request.POST.get('country').strip()
        phone_number = request.POST.get('phone_number').strip()
        status = request.POST.get('status') == "on"

        
        if not name or not house_name or not street_name or not pin_number or not district or not state or not country or not phone_number:
            messages.error(request, "All fields are required.")
            return redirect('user_panel:user_dash')

        
        if not pin_number.isdigit() or len(pin_number) != 6:
            messages.error(request, "Please enter a valid 6-digit PIN number.")
            return redirect('user_panel:user_dash')

        
        if not phone_number.isdigit() or len(phone_number) not in [10, 12]:
            messages.error(request, "Please enter a valid phone number with 10 or 12 digits.")
            return redirect('user_panel:user_dash')

        
        address = UserAddress.objects.create(
            user=users,
            name=name,
            house_name=house_name,
            street_name=street_name,
            pin_number=pin_number,
            district=district,
            state=state,
            country=country,
            phone_number=phone_number,
            status=status,
        )
        address.save()
        messages.success(request, 'Address Added Successfully')
        return redirect('cart:cart_checkout')


class MakeAsDefault(LoginRequiredMixin, View):
    def get(self, request, pk):
        user = request.user
        
        address = get_object_or_404(UserAddress, id=pk, user=user)
        
        updated_count = UserAddress.objects.filter(user=user).update(status=False)
        
        address.status = True
        address.updated_at = timezone.now()
        address.save()
        messages.success(request, 'Default Address set successfully')
        return redirect('user_panel:user_dash')



class AddressDelete(LoginRequiredMixin, View):
    def post(self, request, pk):
        address = get_object_or_404(UserAddress, id=pk) 
        address.is_deleted=True
        address.save()
        messages.success(request, 'Address Deleted Successfully')
        return redirect('user_panel:user_dash')



class ToggleAddressStatus(LoginRequiredMixin, View):
    def post(self, request):
        try:
            address_id = request.POST.get('address_id')
            address = get_object_or_404(UserAddress, id=address_id, user=request.user,is_deleted=False)
            
            # Set all addresses to inactive
            UserAddress.objects.filter(user=request.user).update(order_status=False)
            
            # Set the selected address to active
            address.order_status = True
            address.save()
            
            return JsonResponse({'success': True})
        except UserAddress.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Address not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
        

class UserInvoice(View):
    def get(self, request,pk):
        order_main = OrderMain.objects.get(id=pk)
        order_sub = OrderSub.objects.filter(main_order=order_main,is_active=True)
        return render(request, 'user_dashboard/user_invoice.html',{'order_main':order_main, 'order_sub':order_sub})
    

# def download_invoice_pdf(request, order_id):
#     # Fetch the order details from the database
#     order_main = get_object_or_404(OrderMain, pk=order_id)
#     order_sub = OrderSub.objects.filter(order_main=order_main)

#     # Render the HTML template with the context data
#     html_string = render_to_string('user_dashboard/user_invoice.html', {'order_main': order_main, 'order_sub': order_sub})

#     # Generate the PDF
#     html = HTML(string=html_string)
#     pdf_file = html.write_pdf()

#     # Create the response as a PDF file
#     response = HttpResponse(pdf_file, content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="invoice_{order_main.order_id}.pdf"'

#     return response
