from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from .models import *
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from Accounts.models import Accounts
from Accounts.forms import RegistrationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from orders.models import *
# Create your views here.


#---------------------------------------------- admin login -------------------------------------------------------------#


class AdminLogin(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'Accounts/admin_side/admin_login.html')
    
    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        
        admin = authenticate(request, email=email, password=password)
        
        if admin is not None:
            if admin.is_admin:
                auth_login(request, admin)
                return redirect('admin_panel:admin_dash')
            else:
                messages.error('Please log in with your admin credentials to access the admin dashboard. If you encounter any issues, contact the support team')
        else:
            messages.error(request, 'Invalid username or password.')
        return render(request, 'Accounts/admin_side/admin_login.html')


#---------------------------------------------- admin dash -------------------------------------------------------------#


class Admin(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'Accounts/admin_side/admin.html')
        else:
            return redirect('admin_panel:admin_login')
            
    
def logout(request):
    auth_logout(request)
    return redirect('admin_panel:admin_login')    



#---------------------------------------------- users -------------------------------------------------------------#


class AdminUsers(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.is_authenticated:
            users = Accounts.objects.filter(is_admin=False)
            return render(request, 'Accounts/admin_side/admin_users.html', {'users':users})
        else:
            return render(request, 'Accounts/admin_side/admin_login.html')


#---------------------------------------------- user block -------------------------------------------------------------#

class UserBlock(LoginRequiredMixin, View):
    def get(self, request, pk):
        user_block = get_object_or_404(Accounts, pk=pk)
        user_block.is_blocked = not user_block.is_blocked  # Toggle the blocked status
        user_block.save()
        return redirect('admin_panel:admin_view')
    
#---------------------------------------------- user delete -------------------------------------------------------------#

class UserDelete(View):
    def get(self, request, pk):
        user_delete = get_object_or_404(Accounts, pk=pk)
        user_delete.is_active = not user_delete.is_active  # Toggle the blocked status
        user_delete.save()
        return redirect('admin_panel:admin_view')
    

class OrderStatus(View):
    def post(self, request, pk):
        fk = pk
        order = get_object_or_404(OrderMain, id=pk)
        new_status = request.POST.get('order_status')
        
        if new_status:
            order.order_status = new_status
            order.save()
            
            return redirect('order:admin_orders_details',fk)
        else:
            return HttpResponse("No status selected", status=400)