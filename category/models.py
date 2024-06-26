from django.db import models
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=50)
    description = models.CharField(max_length=500,blank=True)
    is_deleted = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.slug   = slugify(self.category_name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.category_name