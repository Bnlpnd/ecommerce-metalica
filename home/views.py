from django.shortcuts import render
from django.http import HttpResponse
from products.models import Product

def index(request):
    context = {'products' : Product.objects.all()}
    return render(request , 'home/home.html')