from django.db import models
from Accounts.models import *
from products.models import *
from user_panel.models import *

# Create your models here.

class OrderAddress(models.Model):
    name = models.CharField(max_length=50, null=False)
    house_name = models.CharField(max_length=500, null=False)
    street_name = models.CharField(max_length=500, null=False)
    pin_number = models.IntegerField(null=False)
    district = models.CharField(max_length=300, null=False)
    state = models.CharField(max_length=300, null=False)
    country = models.CharField(max_length=50, null=False, default="null")
    phone_number = models.CharField(max_length=50, null=False)
    

class OrderMain(models.Model):
    user = models.ForeignKey(Accounts,  on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(OrderAddress, on_delete=models.SET_NULL, null=True)
    total_amount = models.FloatField(null=False)
    date = models.DateField(auto_now_add=True)
    order_status = models.CharField( max_length=100, default="Order Placed")
    payment_option = models.CharField(max_length=100, default="Cash_on_delivery")
    order_id = models.CharField(max_length=100)
    coupon = models.IntegerField( null=True)
    is_active = models.BooleanField(default=True)
    payment_status = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=50)
    

class OrderSub(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    main_order = models.ForeignKey(OrderMain, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    price = models.FloatField(null=False, default=0)
    quantity = models.IntegerField(null=False, default=0)
    is_active = models.BooleanField(default=True)
    
    def total_cost(self):
        return self.quantity * self.variant.product.offer_price
    


