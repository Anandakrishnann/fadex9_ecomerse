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

# Create your views here.



#---------------------------------------------- User Address Page -------------------------------------------------------------#


class UserDashboard(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        user_data = Accounts.objects.get(email=user.email)
        user_address = UserAddress.objects.filter(user=user, status=True)
        orders = OrderMain.objects.filter(user=request.user.id)
        order_sub = OrderSub.objects.filter(user=request.user.id)
        
        balance = 0  # Initialize balance to 0 by default
        wallets = None  # Initialize wallets to None by default
        try:
            wallets = Wallet.objects.get(user=user)
            balance = wallets.balance
        except Wallet.DoesNotExist:
            messages.error(request, "User doesn't have a wallet")
        
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
        return render(request, 'user_dashboard/edit_user_details.html', {'user':user})
    
    def post(self, request, pk):
        user = Accounts.objects.get(id=pk)
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        
        user.save()
        
        return redirect('user_panel:user_dash')
        

class ChangePassword(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_dashboard/change_password.html')
    
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

        return render(request, 'user_dashboard/change_password.html')


class CreateAddress(LoginRequiredMixin, View):
    def post(self, request):
        users = request.user
        name = request.POST.get('name')
        house_name = request.POST.get('house_name')
        street_name = request.POST.get('street_name')
        pin_number = request.POST.get('pin_number')
        district  = request.POST.get('district')
        state = request.POST.get('state')
        country = request.POST.get('country')
        phone_number = request.POST.get('phone_number')
        status = request.POST.get('status') == "on"
        
        address = UserAddress.objects.create(
            user = users,
            name = name,
            house_name = house_name,
            street_name = street_name,
            pin_number = pin_number,
            district = district,
            state = state,
            country = country,
            phone_number = phone_number,
            status = status,
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
        users.name = request.POST.get('name')
        users.house_name = request.POST.get('house_name')
        users.street_name = request.POST.get('street_name')
        users.pin_number = request.POST.get('pin_number')
        users.district  = request.POST.get('district')
        users.state = request.POST.get('state')
        users.country = request.POST.get('country')
        users.phone_number = request.POST.get('phone_number')
        
        if users.status:
            updated_count = UserAddress.objects.filter(user=users.user).update(status=False)
            users.status = request.POST.get('status') == "on"
        
            users.save()

        return redirect('user_panel:user_dash')


class AddAddress(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_dashboard/add_new_address.html' )
    
    def post(self, request):
        users = request.user
        name = request.POST.get('name')
        house_name = request.POST.get('house_name')
        street_name = request.POST.get('street_name')
        pin_number = request.POST.get('pin_number')
        district  = request.POST.get('district')
        state = request.POST.get('state')
        country = request.POST.get('country')
        phone_number = request.POST.get('phone_number')
        status = request.POST.get('status') == "on"
        
        address = UserAddress.objects.create(
            user = users,
            name = name,
            house_name = house_name,
            street_name = street_name,
            pin_number = pin_number,
            district = district,
            state = state,
            country = country,
            phone_number = phone_number,
            status = status,
        )
        
        address.save()
        return redirect('cart:cart_checkout')
    
        
class MakeAsDefault(LoginRequiredMixin, View):
    def get(self, request, pk):
        user = request.user
        
        address = get_object_or_404(UserAddress, id=pk, user=user)
        
        updated_count = UserAddress.objects.filter(user=user).update(status=False)
        
        address.status = True
        address.save()
        
        return redirect('user_panel:user_dash')
    
class AddressDelete(LoginRequiredMixin, View):
    def post(self, request, pk):
        address = get_object_or_404(UserAddress, id=pk) 
        address.status=False
        address.save()
        
        return redirect('user_panel:user_dash')
    
    
class ToggleAddressStatus(LoginRequiredMixin, View):
    def post(self, request):
        try:
            address_id = request.POST.get('address_id')
            address = get_object_or_404(UserAddress, id=address_id, user=request.user)
            
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