from django.shortcuts import render, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def galeria_view(request):
    productos = Product.objects.all()
    producto_seleccionado = request.GET.get('producto')
    
    if producto_seleccionado:
        modelos = ProductMaterial.objects.filter(product_id=producto_seleccionado)
    else:
        modelos = ProductMaterial.objects.all()
        producto_seleccionado = None

    modelos_con_datos = []
    for modelo in modelos:
        imagen = modelo.product_images.first() if modelo else None
        modelos_con_datos.append({
            'modelo': modelo,
            'imagen': imagen
        })

    contexto = {
        'productos': productos,
        'producto_seleccionado': producto_seleccionado,
        'modelos': modelos_con_datos
    }
    return render(request, 'product/galeria.html', contexto)


def detalle_producto(request, uid):
    modelo = get_object_or_404(ProductMaterial, uid=uid)
    imagen = modelo.product_images.first() if modelo else None

    return render(request, 'product/detalleproduct.html', {
        'modelo': modelo,
        'imagen': imagen
    })
    
@login_required
def proforma_view(request):
    productos = Product.objects.all()
    return render(request, 'product/proforma.html', {
        'productos': productos
    })

def obtener_modelos_por_tipo(request):
    product_id = request.GET.get('product_id')
    print("DEBUG tipo_id recibido:", product_id)
    
    # Verifica que product_id no sea vacío
    if not product_id:
        return JsonResponse({'error': 'product_id vacío'}, status=400)

    modelos = ProductMaterial.objects.filter(product_id=product_id)
    print(f"Modelos filtrados: {[m.productmaterial_name for m in modelos]}")

    data = []
    for modelo in modelos:
        imagen = modelo.product_images.first() if modelo else None
        imagen_url = imagen.image.url if imagen else ''

        data.append({
            'id': str(modelo.uid),
            'nombre': modelo.productmaterial_name,
            'imagen_url': imagen_url
        })

    print("Modelos devueltos:", data)  # VERIFICA ESTO EN CONSOLA
    return JsonResponse({'modelos': data})