from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from django.views import View
from django.contrib import messages
from Accounts.models import *

# Create your views here.



#---------------------------------------------- User Address Page -------------------------------------------------------------#


class UserDashboard(View):
    def get(self, request):
        user_address = UserAddress.objects.filter(user=request.user)
        return render(request, 'user_dashboard/user_dash.html',{'user_address': user_address})
    

class CreateAddress(View):
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



class EditAddress(View):
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
                users.status = request.POST.get('status') == "on"
            
            users.save()

            return redirect('user_panel:user_dash')
        
class MakeAsDefault(View):
    def get(self, request, pk):
        user = request.user
        
        address = get_object_or_404(UserAddress, id=pk, user=user)
        
        updated_count = UserAddress.objects.filter(user=user).update(status=False)
        
        address.status = True
        address.save()
        
        return redirect('user_panel:user_dash')
    
class AddressDelete(View):
    def post(self, request, pk):
        address = get_object_or_404(UserAddress, id=pk) 
        address.delete()
        
        return redirect('user_panel:user_dash')