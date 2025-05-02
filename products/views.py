from pydoc import render_doc
from tkinter import E
from django.shortcuts import render
from .models import Product
        
def product(request):
    return render(request ,'product/tipo_puerta.html')