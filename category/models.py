from django.db import models

# Create your models here.

class Category(models.Model):
    Category_name = models.CharField(max_length=50, unique=True)
    Slug = models.CharField(max_length=50)
    description = models.CharField(max_length=500,blank=True)
    cat_image = models.ImageField(upload_to='static/categories',blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.Category_name