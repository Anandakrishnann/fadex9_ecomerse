import json
import logging
from Accounts.models import *
from products.models import *
from cart.models import *
from user_panel.models import *
from django.http import JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from django.views import View
from django.contrib import messages
from Accounts.models import *
from orders.models import *

# Create your views here.


class WishlistView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            user = request.user.id
            wishlists = Wishlist.objects.filter(user=user)
            return render(request, 'user_dashboard/wishlist.html', {'wishlists':wishlists})
        except:
            return render(request, 'user_dashboard/wishlist.html')
    
    


class AddToWishlist(LoginRequiredMixin, View):
    def post(self, request):
        variant_id = request.POST.get('variant')
        if not variant_id :
            return JsonResponse({'message': 'Something error '}, status=400)
        if variant_id:
            try:
                user = get_object_or_404(Accounts, id=request.user.id)
                variant = get_object_or_404(ProductVariant, id=variant_id)
                
                wishlist, created = Wishlist.objects.get_or_create(user=user, variant=variant)
                
                message = 'Product added to wishlist' if created else 'Product is already in your wishlist'
                return JsonResponse({'message': message},status=200)

            except Exception as e:
                return JsonResponse({'message': f'Error: {e}'}, status=500)


class RemoveWishlist(LoginRequiredMixin,View):
    def post(self, request, pk):
        try:
            item = get_object_or_404(Wishlist, id=pk)
            item.delete()
            return JsonResponse({'success': True, 'message': 'Product Removed Successfully'})
        except Wishlist.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})
