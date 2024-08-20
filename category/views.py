from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from .forms import CategoryForm
from .models import Category
from django.utils.decorators import method_decorator
from utils.decorators import admin_required
from shared.mixins import PreventBackMixin  # Import the mixin
from django.core.paginator import Paginator


# Create your views here.


@method_decorator(admin_required, name='dispatch')

class CreateCategory(PreventBackMixin,View):
    def get(self, request):
        form = CategoryForm()
        return render(request, 'Category/create_category.html', {'form': form})

    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('category:category')
        else:
            # Capture all form errors and add them to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        return render(request, 'Category/create_category.html', {'form': form})



@method_decorator(admin_required, name='dispatch')
class CategoryList(PreventBackMixin,View):
    def get(self, request):
        if request.user.is_authenticated:
            query = request.GET.get('q')
            if query:
                categories = Category.objects.filter(category_name__icontains=query)
            else:
                categories = Category.objects.all()
            
            paginator = Paginator(categories, 4)  # Show 10 return requests per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'Category/category.html', {'categories': page_obj, 'query': query})
        else:
            return render(request, 'Accounts/admin_side/admin_login.html')
        
        
@method_decorator(admin_required, name='dispatch')
class CategoryEdit(PreventBackMixin,View):
    def get(self, request, pk):
        category = get_object_or_404(Category, id=pk)
        form = CategoryForm(instance=category)
        return render(request, 'Category/edit_category.html',{'form':form, 'category':category})
    
    def post(self, request, pk):
        category = get_object_or_404(Category, id=pk)
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category Edited Successfully')
            return redirect('category:category')
        else:
            # Capture all form errors and add them to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
                    
        return render(request, 'Category/edit_category.html', {'form': form, 'category': category})
    
    
@method_decorator(admin_required, name='dispatch')
class DeleteCategory(PreventBackMixin,View):
    def get(self, request, pk):
        delete_category = get_object_or_404(Category, id=pk)
        delete_category.is_deleted = not delete_category.is_deleted
        delete_category.save()
        messages.success(request, 'Status Updated Successfully')
        return redirect('category:category')