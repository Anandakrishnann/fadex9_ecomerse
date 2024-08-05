from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from .forms import CategoryForm
from .models import Category
from django.utils.decorators import method_decorator
from utils.decorators import admin_required


# Create your views here.


@method_decorator(admin_required, name='dispatch')
class CreateCategory(View):
    def get(self, request):
        form = CategoryForm
        return render(request, 'Category/create_category.html', {'form':form})
    
    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category:category')
        return render(request, 'Category/create_category.html', {'form':form})

@method_decorator(admin_required, name='dispatch')
class CategoryList(View):
    def get(self, request):
        if request.user.is_authenticated:
            query = request.GET.get('q')
            if query:
                categories = Category.objects.filter(category_name__icontains=query, is_deleted=False)
            else:
                categories = Category.objects.filter(is_deleted=False)
            return render(request, 'Category/category.html', {'categories': categories, 'query': query})
        else:
            return render(request, 'Accounts/admin_side/admin_login.html')
@method_decorator(admin_required, name='dispatch')
class CategoryEdit(View):
    def get(self, request, pk):
        category = get_object_or_404(Category, id=pk)
        form = CategoryForm(instance=category)
        return render(request, 'Category/edit_category.html',{'form':form, 'category':category})
    
    def post(self, request, pk):
        category = get_object_or_404(Category, id=pk)
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category:category')
        return render(request, 'Category/edit_category.html', {'form': form, 'category': category})
@method_decorator(admin_required, name='dispatch')
class DeleteCategory(View):
    def get(self, request, pk):
        delete_category = get_object_or_404(Category, id=pk)
        delete_category.is_deleted = not delete_category.is_deleted
        delete_category.save()
        return redirect('category:category')