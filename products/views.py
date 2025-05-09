from django.shortcuts import render
from pydoc import render_doc
from tkinter import E
from django.shortcuts import render
from .models import Tipo, Product, ProductImage

 
def galeria_view(request):
    tipos = Tipo.objects.all()
    tipo_seleccionado = request.GET.get('tipo')
    
    if tipo_seleccionado:
        productos = Product.objects.filter(tipo_id=tipo_seleccionado)
    else:
        productos = Product.objects.all()
    
    contexto = {
        'tipos': tipos,
        'productos': productos,
        'tipo_seleccionado': int(tipo_seleccionado) if tipo_seleccionado else None,
    }
    return render(request, 'product/galeria.html', contexto)