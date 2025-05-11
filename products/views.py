from django.shortcuts import render
from .models import Tipo, Product

def galeria_view(request):
    tipos = Tipo.objects.all()
    tipo_seleccionado = request.GET.get('tipo')
    
    if tipo_seleccionado:
        productos = Product.objects.filter(tipo__uid=tipo_seleccionado)
    else:
        productos = Product.objects.all()
        tipo_seleccionado = None
    
    contexto = {
        'tipos': tipos,
        'productos': productos,
        'tipo_seleccionado': tipo_seleccionado,
    }
    return render(request, 'product/galeria.html', contexto)
