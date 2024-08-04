from django.http import JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from django.views import View
from django.contrib import messages
from Accounts.models import *
from orders.models import *
from django.contrib.auth import authenticate, login


# Create your views here.

# class Wallet(View, LoginRequiredMixin):
#     def get(self, request):
        