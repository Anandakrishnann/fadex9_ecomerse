from django.db import models
from Accounts.models import *
from products.models import *

# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.user

class CartItem(models.Model):   
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart")
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def total_amount(self):
        return self.variant.product.offer_price * self.quantity
    
    def sub_total(self):
        return self.product.offer_price * self.quantity

    def _str_(self):
        return self.product