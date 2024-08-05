from functools import wraps 
from django.shortcuts import redirect 
from django.contrib import messages 
from django.contrib.auth.decorators import login_required 
from django.http import HttpResponseRedirect
from django.urls import reverse

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is trying to access the admin login page
        if request.path == reverse('admin_panel:admin_login'):
            return view_func(request, *args, **kwargs)

        # Check if the user is authenticated and is an admin
        if not request.user.is_staff or not request.user.is_admin:
            return HttpResponseRedirect(reverse('admin_panel:admin_login'))
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view