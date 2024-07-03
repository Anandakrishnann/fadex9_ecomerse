from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']
        widgets = {
            'category_name': forms.TextInput(attrs={'placeholder': 'Type here', 'class': 'form-control', 'maxlength': 50}),
            'description': forms.Textarea(attrs={'placeholder': 'Type here', 'class': 'form-control', 'rows': 4, 'maxlength': 500}),
        }
        labels = {
            'category_name': 'Category Name',
            'description': 'Description',
        }