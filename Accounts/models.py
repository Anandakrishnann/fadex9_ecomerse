from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager): 
    def create_user(self, email, first_name, last_name, phone_number, password=None): 
        if not email: 
            raise ValueError('Users must have an email address') 
        email = self.normalize_email(email) 
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name, 
            phone_number=phone_number
        ) 
        user.set_password(password) 
        user.is_active = False  # User is not active until they verify their OTP 
        user.is_blocked = False 
        user.date_joined = timezone.now()  # Set the date_joined field 
        user.save(using=self._db) 
        return user 
    def create_superuser(self, email, first_name, last_name, phone_number, password=None): 
        user = self.create_user(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            password = password,
            phone_number = phone_number
        ) 
        user.is_admin = True 
        user.is_staff = True 
        user.is_active = True  
        user.date_joined = timezone.now()  
        user.save(using=self._db) 
        return user

class Accounts(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    is_active = models.BooleanField(default=False)  
    is_admin = models.BooleanField(default=False)  
    is_staff = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)  
    date_joined = models.DateTimeField(default=timezone.now)  

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','phone_number']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    
    @property
    def username(self):
        return f"{self.first_name} {self.last_name}"
    

class UserProfile(models.Model):
    user = models.OneToOneField("Accounts", on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank=True, max_length=50)
    
    

