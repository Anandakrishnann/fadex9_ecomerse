from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from .models import *
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from Accounts.models import Accounts
from Accounts.forms import RegistrationForm
# Create your views here.


#---------------------------------------------- admin login -------------------------------------------------------------#


class Admin_Login(View):
    def get(self, request):
        return render(request, 'Accounts/admin_side/admin_login.html')
    
    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        
        admin = authenticate(request, email=email, password=password)
        
        if admin is not None:
            if admin.is_admin:
                auth_login(request, admin)
                return redirect('admin_dash')
            else:
                messages.error('Please log in with your admin credentials to access the admin dashboard. If you encounter any issues, contact the support team')
        else:
            messages.error(request, 'Invalid username or password.')
        return render(request, 'Accounts/admin_side/admin_login.html')


#---------------------------------------------- admin dash -------------------------------------------------------------#


class Admin_dash(View):
    def get(self, request):
        return render(request, 'Accounts/admin_side/admin_view.html')


#---------------------------------------------- users -------------------------------------------------------------#


class Admin_Users(View):
    def get(self, request):
        users = Accounts.objects.filter(is_admin=False)
        return render(request, 'Accounts/admin_side/admin_users.html', {'users':users})


#---------------------------------------------- create user -------------------------------------------------------------#


class Create_User(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'Accounts/admin_side/admin_create.html',{'form':form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False) 
            user.set_password(form.cleaned_data['password'])  # Set the user's password 
            user.save() 
            messages.success(request, 'User created successfully.') 
            return redirect('admin_view')
        
        return render(request, 'Accounts/admin_side/admin_create.html', {'form': form})
    
    
#---------------------------------------------- user block -------------------------------------------------------------#

class User_Block(View):
    def get(self, request, pk):
        user_block = get_object_or_404(Accounts, pk=pk)
        user_block.is_blocked = not user_block.is_blocked  # Toggle the blocked status
        user_block.save()
        return redirect('admin_view')
    

#---------------------------------------------- user block -------------------------------------------------------------#

class User_Unblock(View):
    def get(self, request, pk):
        user_unblock = Accounts.objects.get(pk=pk)
        user_unblock.is_blocked = True
        user_unblock.save()
        return redirect('admin_view')
    

#---------------------------------------------- user delete -------------------------------------------------------------#

class User_Delete(View):
    def get(self, request, pk):
        user_unblock = Accounts.objects.get(pk=pk)
        user_unblock.is_active = False
        user_unblock.save()
        return redirect('admin_view')
    
