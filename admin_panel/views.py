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
from django.db.models import *
from datetime import datetime
from django.utils.decorators import method_decorator
from utils.decorators import admin_required
from datetime import datetime, timedelta


# Create your views here.


#---------------------------------------------- admin login -------------------------------------------------------------#


@method_decorator(admin_required, name='dispatch')
class AdminLogin(View):
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

@method_decorator(admin_required, name='dispatch')
class AdminDash( View):
    def get(self, request):
        total_order_amount = OrderMain.objects.filter(order_status="Order Placed").aggregate(total=Sum('total_amount'))['total'] or 0
        total_order_count = OrderMain.objects.filter(order_status="Order Placed").aggregate(total_orders=Count('id'))['total_orders'] or 0
        total_discount = OrderMain.objects.filter(order_status="Order Placed").aggregate(
            total_discount=Sum(F('discount_amount'))
        )['total_discount'] or 0
        
        now = timezone.now()
        current_year = now.year
        current_month = now.month
        
        monthly_earnings = OrderMain.objects.filter(
            order_status="Order Placed",
            date__year=current_year,
            date__month=current_month
        ).aggregate(monthly_total=Sum('total_amount'))['monthly_total'] or 0
        
        return render(request, 'Accounts/admin_side/admin.html',{'total_order_amount':total_order_amount, 'total_order_count':total_order_count,'total_discount':total_discount,'monthly_earnings':monthly_earnings})


def logout(request):
    auth_logout(request)
    return redirect('admin_panel:admin_login')   



#---------------------------------------------- users -------------------------------------------------------------#

@method_decorator(admin_required, name='dispatch')
class AdminUsers(View):
    def get(self, request):
        if request.user.is_authenticated:
            query = request.GET.get('q')
            if query:
                users = Accounts.objects.filter(email__icontains=query)
            else:
                users = Accounts.objects.filter(is_admin=False)
            return render(request, 'Accounts/admin_side/admin_users.html', {'users':users})
        else:
            return render(request, 'Accounts/admin_side/admin_login.html')


#---------------------------------------------- user block -------------------------------------------------------------#
@method_decorator(admin_required, name='dispatch')
class UserBlock(View):
    def get(self, request, pk):
        user_block = get_object_or_404(Accounts, pk=pk)
        user_block.is_blocked = not user_block.is_blocked  # Toggle the blocked status
        user_block.save()
        return redirect('admin_panel:admin_view')
    
#---------------------------------------------- user delete -------------------------------------------------------------#
@method_decorator(admin_required, name='dispatch')
class UserDelete(View):
    def get(self, request, pk):
        user_delete = get_object_or_404(Accounts, pk=pk)
        user_delete.is_active = not user_delete.is_active  # Toggle the blocked status
        user_delete.save()
        return redirect('admin_panel:admin_view')
    
@method_decorator(admin_required, name='dispatch')
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
        
        
        
@method_decorator(admin_required, name='dispatch')
class SalesReport(View):
    def get(self, request):
        filter_type = request.GET.get('filter', None)

        now = timezone.now()
        start_date = end_date = None  # Initialize to None

        if filter_type == 'weekly':
            start_date = now - timedelta(days=now.weekday())
            end_date = now
        elif filter_type == 'monthly':
            start_date = now.replace(day=1)
            end_date = now

        # Filter orders based on whether a date range is defined
        if start_date and end_date:
            orders = OrderMain.objects.filter(
                order_status="Order Placed",
                is_active=True,
                date__range=[start_date, end_date]
            )
        else:
            # No specific filter, show all "Order Placed" orders
            orders = OrderMain.objects.filter(
                order_status="Order Placed",
                is_active=True
            )

        total_discount = orders.aggregate(total=Sum('discount_amount'))['total']
        total_orders = orders.aggregate(total=Count('id'))['total']
        total_order_amount = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        return render(request, 'Accounts/admin_side/sales_report.html', {
            'orders': orders,
            'total_discount': total_discount,
            'total_orders': total_orders,
            'total_order_amount': total_order_amount
        })
    
    
@method_decorator(admin_required, name='dispatch')
class OrderDateFilter(View):
    def post(self, request):
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if start_date and end_date:
            
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                
            except ValueError:
                return redirect('admin_panel:sales_report')
            
            orders = OrderMain.objects.filter(date__range=[start_date,end_date], order_status="Order Placed")
            total_discount = orders.aggregate(total=Sum('discount_amount'))['total']
            total_orders = orders.aggregate(total=Count('id'))['total']
            total_order_amount = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            
            return render(request, 'Accounts/admin_side/sales_report.html',{'orders':orders,'total_discount':total_discount,'total_orders':total_orders,'total_order_amount':total_order_amount})
        
        return redirect('admin_panel:sales_report')
    


