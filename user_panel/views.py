from django.shortcuts import render,redirect, get_object_or_404
from .models import *
from django.views import View
from django.contrib import messages
from Accounts.models import *

# Create your views here.



#---------------------------------------------- User Address Page -------------------------------------------------------------#


class Address(View):
    def post(self, request, pk):
        users = get_object_or_404(Accounts, id=pk)
        name = request.POST.get('name')
        house_name = request.POST.get('house_name')
        street_name = request.POST.get('street_name')
        pin_number = request.POST.get('pin_number')
        district  = request.POST.get('district')
        state = request.POST.get('state')
        country = request.POST.get('country')
        phone_number = request.POST.get('phone_number')
        status = request.POST.get('status')
        
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
        messages.success('Your address has been successfully created')
        address.save()
        return redirect('accounts:user_dashboard')
