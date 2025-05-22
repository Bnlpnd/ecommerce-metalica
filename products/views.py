from django.shortcuts import render, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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


def detalle_producto(request, uid):
    producto = get_object_or_404(Product, uid=uid)
    materiales = ProductMaterial.objects.filter(product=producto)
    imagen = producto.product_images.first()  # Obtiene la primera imagen asociada

    return render(request, 'product/detalleproduct.html', {
        'producto': producto,
        'materiales': materiales,
        'imagen': imagen
    })
    
@login_required
def proforma_view(request):
    tipos_puerta = Tipo.objects.all()
    return render(request, 'product/proforma.html', {
        'tipos_puerta': tipos_puerta,
    })

def obtener_modelos_por_tipo(request):
    tipo_id = request.GET.get('tipo_id')
    print("DEBUG tipo_id recibido:", tipo_id)
    
    # Verifica que tipo_id no sea vacío
    if not tipo_id:
        return JsonResponse({'error': 'tipo_id vacío'}, status=400)


    productos = Product.objects.filter(tipo__uid=tipo_id)
    print(f"Productos filtrados: {[p.product_name for p in productos]}")

    
    data = []
    for producto in productos:
        imagen = producto.product_images.first()
        imagen_url = imagen.image.url if imagen else ''

        #modelos = ProductMaterial.objects.filter(product=producto)

        data.append({
            'id': str(producto.uid),
            'nombre': producto.product_name,
            'imagen_url': imagen_url
        })

    print("Modelos devueltos:", data)  # VERIFICA ESTO EN CONSOLA
    return JsonResponse({'modelos': data})