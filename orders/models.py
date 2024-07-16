from django.db import models
from Accounts.models import *
from user_panel.models import *

# Create your models here.

# class Order(models.Model):
#     user = models.ForeignKey(Accounts,  on_delete=models.SET_NULL, null=True)
#     address = models.ForeignKey(UserAddress, on_delete=models.SET_NULL,null=True)
#     payment = 