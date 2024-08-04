from django.db import models
from Accounts.models import *
from django.db.models import *

# Create your models here.

class Wallet(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateField(auto_now_add=True)

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE)
    description = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type=models.CharField(max_length=500)