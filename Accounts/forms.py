from django import forms
from django.core.exceptions import ValidationError
from .models import Accounts
from django.contrib.auth import authenticate
import re
from django.contrib.auth.forms import AuthenticationForm

class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True)

    class Meta:
        model = Accounts
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            first_name = first_name.strip()  # Strip leading and trailing whitespace

            # Check for spaces
            if ' ' in first_name:
                raise ValidationError("First name cannot contain spaces")
            
            # Ensure no special characters or digits
            if not first_name.isalpha():
                raise ValidationError("First name must contain only letters")
            
            # Ensure minimum length
            if len(first_name) < 2:
                raise ValidationError("First name must be at least 2 characters long")
            
            # Ensure maximum length
            if len(first_name) > 50:
                raise ValidationError("First name cannot be longer than 50 characters")
            
            # Check for specific forbidden characters (example: no hyphens or underscores)
            forbidden_characters = ['-', '_']
            if any(char in forbidden_characters for char in first_name):
                raise ValidationError(f"First name cannot contain any of the following characters: {' '.join(forbidden_characters)}")


        return first_name


    def clean_last_name(self):

        last_name = self.cleaned_data.get('last_name')

        if last_name:
            last_name = last_name.strip()  # Strip leading and trailing whitespace

            # Check for spaces
            if ' ' in last_name:
                raise ValidationError("Last name cannot contain spaces")
            
            # Ensure no special characters or digits
            if not last_name.isalpha():
                raise ValidationError("Last name must contain only letters")
            
            # Ensure minimum length
            if len(last_name) < 2:
                raise ValidationError("Last name must be at least 2 characters long")
            
            # Ensure maximum length
            if len(last_name) > 50:
                raise ValidationError("Last name cannot be longer than 50 characters")
            
            # Check for specific forbidden characters (example: no hyphens or underscores)
            forbidden_characters = ['-', '_']
            if any(char in forbidden_characters for char in last_name):
                raise ValidationError(f"Last name cannot contain any of the following characters: {' '.join(forbidden_characters)}")


        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            phone_number = phone_number.strip()  # Strip leading and trailing whitespace
            
            # Ensure the phone number is exactly 10 digits
            if not re.match(r'^\d{10}$', phone_number):
                raise ValidationError("Phone number must be exactly 10 digits.")

        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # we check that the email is unique
        if Accounts.objects.filter(email=email).exists():
            raise ValidationError("Email is already in use.")
        return email

    def clean_password(self):
        cleaned_data = super().clean()
        password = self.cleaned_data.get('password')

        if not password:
            raise forms.ValidationError("Password requires minimum 8 characters")

        # Check if password contains at least 8 digit
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        # Check if password contains at least one digit
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must contain at least one numeric character.")

        # Check if password contains at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")

        # Check if password contains at least one lowercase letter
        if not any(char.islower() for char in password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")

        # Check if password contains at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("Password must contain at least one special character.")

        # Check for whitespaces in the password
        if ' ' in password:
            raise forms.ValidationError("Password cannot contain whitespaces.")

        return password
    
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        print(password)
        confirm_password = self.cleaned_data.get('confirm_password')
        print(confirm_password)

        if password is None:
        # Password did not pass the previous validation, no need to compare
            return confirm_password

        # Check if passwords match
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return confirm_password


class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'placeholder': 'Enter OTP'}))


class EmailAuthenticationForm(AuthenticationForm): 
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'})) 
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
