from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']

        widgets = {
            'category_name': forms.TextInput(attrs={'maxlength': 50}),
            'description': forms.Textarea(attrs={'maxlength': 500}),
        }