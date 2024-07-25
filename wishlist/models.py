from django.db import models
from Accounts.models import *
from products.models import *

# Create your models here.

class Wishlist(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)