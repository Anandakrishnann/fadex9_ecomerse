from django.http import JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from django.views import View
from django.contrib import messages
from Accounts.models import *

# Create your views here.



#---------------------------------------------- User Address Page -------------------------------------------------------------#


class UserDashboard(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        user_address = UserAddress.objects.filter(user=user, status=True)
        return render(request, 'user_dashboard/user_dash.html',{'user_address': user_address, 'user':user})
    


class UserDetails(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        try:
            user_details = get_object_or_404(Accounts, email=user)
            return render(request, 'user_dashboard/user_details.html', {'user_details':user_details})
        except:
            return redirect('accounts:login')
    

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
            UserAddress.objects.filter(user=request.user).update(status=False)
            
            # Set the selected address to active
            address.status = True
            address.save()
            
            return JsonResponse({'success': True})
        except UserAddress.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Address not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})