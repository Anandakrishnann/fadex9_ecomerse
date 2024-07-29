from django.db import models

# Create your models here.

class Brand(models.Model):
    
    brand_name = models.CharField(max_length=50, null=False, unique=True)
    brand_image = models.ImageField(upload_to='brand_images')
    description = models.TextField(max_length=500,default=True)
        
    status = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.brand_name