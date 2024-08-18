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
        
    def clean_category_name(self):
            category_name = self.cleaned_data.get('category_name', '').strip()
            instance = self.instance
            
            if not category_name:
                raise forms.ValidationError('Category name cannot be empty.')

            
            if Category.objects.filter(category_name__iexact=category_name).exclude(pk=instance.pk).exists():
                raise forms.ValidationError('A category with this name already exists.')

            return category_name


    def clean_description(self):

            description = self.cleaned_data.get('description', '').strip()

            if not description:
                raise forms.ValidationError('Description cannot be empty.')


            return description