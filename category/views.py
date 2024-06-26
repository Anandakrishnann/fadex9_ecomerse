from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from .forms import CategoryForm
from .models import Category

# Create your views here.

class Create_Category(View):
    def get(self, request):
        form = CategoryForm
        return render(request, 'Category/create_category.html', {'form':form})
    
    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category')
        return render(request, 'Category/create_category.html', {'form':form})

class Category_List(View):
    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'Category/category.html',{'categories':categories})
    
class Category_Edit(View):
    def get(self, request, pk):
        category = get_object_or_404(Category, id=pk)
        form = CategoryForm(instance=category)
        return render(request, 'Category/edit_category.html',{'form':form, 'category':category})
    
    def post(self, request, pk):
        category = get_object_or_404(Category, id=pk)
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category')
        return render(request, 'Category/edit_category.html', {'form': form, 'category': category})
    
class Delete_Category(View):
    def get(self, request, pk):
        delete_category = get_object_or_404(Category, id=pk)
        delete_category.is_deleted = True
        delete_category.save()
        return redirect('category')
    
class Restore_Category(View):
    def get(self, request, pk):
        delete_category = get_object_or_404(Category, id=pk)
        delete_category.is_deleted = False
        delete_category.save()
        return redirect('category')