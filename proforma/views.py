from django.http import HttpResponse, HttpResponseForbidden, FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from products.models import Product, ProductMaterial
from django.contrib import messages
from django.conf import settings
BASE_DIR = settings.BASE_DIR
import joblib
import os
from reportlab.pdfgen import canvas
from io import BytesIO
from django.core.files.base import ContentFile
import pandas as pd
from django.utils.text import slugify
from datetime import date

@login_required
def solicitar_cotizacion(request, product_uid):
    producto = get_object_or_404(Product, uid=product_uid)

    if request.method == 'POST':
        form = CotizacionForm(request.POST)
        if form.is_valid():
            cotizacion = form.save(commit=False)
            cotizacion.cliente = request.user
            cotizacion.producto = producto
            cotizacion.save()
            messages.success(request, 'Se ha mandado la cotización. ¡Muchas gracias por su preferencia!')
            return redirect('galeria')  # o a una página de confirmación
    else:
        form = CotizacionForm()

    return render(request, 'proforma/solicitar_cotizacion.html', {
        'form': form,
        'producto': producto
    })

def ping(request):
    return HttpResponse("Proforma app está funcionando.")

@login_required
def bandeja_cotizaciones(request, cotizacion_id=None):
    # Verifica si el usuario tiene perfil y si es trabajador
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'trabajador':
        return HttpResponseForbidden("Acceso denegado. Esta sección es solo para trabajadores.")

    cotizaciones = Cotizacion.objects.filter(estado='pendiente').order_by('-fecha_creacion')
    
    # VERIFICAR SI HAY COTIZACIONES DISPONIBLES
    if not cotizaciones.exists():
        messages.warning(request, "No hay cotizaciones pendientes.")
        return render(request, 'proforma/bandeja.html', {
            'cotizaciones': [],
            'cotizacion_activa': None,
            'form': None,
            'precio_calculado': None,
            'proforma': None
        })
    
    cotizacion_seleccionada = get_object_or_404(Cotizacion, id=cotizacion_id) if cotizacion_id else cotizaciones.first()

    form = ProformaForm()
    precio_calculado = None  # <- para mostrar en la plantilla
    proforma = None

    if request.method == 'POST':
        form = ProformaForm(request.POST)
        
        if form.is_valid():
            if 'predecir' in request.POST and form.is_valid():
                
                # 1. Diccionario de codificación
                codigos_producto = {
                    'Porton cochera levadizo': 0,
                    'Porton corredizo 2Hojas': 1,
                    'Porton seccional para cochera': 2,
                    'Puerta con aplicaciones en acero inoxidable': 3,
                    'Puerta enrrollable mas enrejado para negocio de 4 Hojas': 4,
                    'Puerta enrrollable mas enrejado para negocio de barras 2 Hojas': 5,
                    'Puerta enrrollable mas enrejado para negocio rombo 4 Hojas': 6,
                    'Puerta enrrollable para negocio': 7,
                    'Puerta interior barras lineales': 8,
                    'Puerta interior con circulos': 9,
                    'Puerta modelo en arco': 10,
                    'Puerta principal estilo madera': 11
                }

                codigos_material = {
                    'Material simple': 0,
                    'Material intermedio': 1,
                    'Material resistente': 2
                }
                
                # 2. Extraer datos
                alto = form.cleaned_data['alto']
                ancho = form.cleaned_data['ancho']

                producto_nombre = cotizacion_seleccionada.producto.product_name
                
                #product_material = cotizacion_seleccionada.producto.products.first() #CAMBIE AHORA _SET
                #material_nombre = product_material.material.material_name if product_material else 'Material simple'

                # material se selecciona desde el formulario (es un ForeignKey a Material)
                material_obj = form.cleaned_data['material']
                material_nombre = material_obj.material_name  # accede al nombre del material

                producto_cod = codigos_producto.get(producto_nombre, 0)
                material_cod = codigos_material.get(material_nombre, 0)
                
                # 3. Preparar y predecir
                datos = pd.DataFrame([[alto, ancho, producto_cod, material_cod]], columns=['alto', 'ancho', 'producto', 'material'])
                modelo_path = os.path.join(BASE_DIR, 'modelo_arbol.pkl')
                print("Entró al modelo")
                print(alto,ancho,producto_cod, producto_nombre, material_cod, material_nombre)
                
                print("📁 Buscando modelo en:", modelo_path)


                if os.path.exists(modelo_path):
                    modelo = joblib.load(modelo_path)
                    print("modelo cargado correctamente:", modelo)

                    # prediccion = modelo.predict(datos)
                    # datos = [[form.cleaned_data['alto'], form.cleaned_data['ancho']]]
                    
                    print("📊 Datos para predecir:")
                    print(datos)
                    print("📊 Columnas:", datos.columns)

                    try:
                        prediccion = modelo.predict(datos)
                        precio_calculado = round(prediccion[0], 2)
                        
                        print("🔍 Precio calculado:", precio_calculado)

                        messages.info(request, f'Precio estimado: S/. {precio_calculado}')
                    except Exception as e:
                        print("❌ Error al predecir:", e)
                        
            elif 'guardar' in request.POST and form.is_valid():
                proforma = form.save(commit=False)
                proforma.cliente = cotizacion_seleccionada.cliente
                #proforma.productmaterial = cotizacion_seleccionada.producto.products.first() #cambie _set
                proforma.preciototal = proforma.precio + proforma.precioinstalacion
                proforma.save()

                # PDF
                buffer = BytesIO()
                p = canvas.Canvas(buffer)
                p.setFont("Helvetica", 12)
                p.drawString(50, 800, f"Proforma N°: {proforma.proforma_num}")
                p.drawString(50, 780, f"Cliente: {proforma.cliente.username}")
                p.drawString(50, 760, f"Alto: {proforma.alto}")
                p.drawString(50, 740, f"Ancho: {proforma.ancho}")
                p.drawString(50, 720, f"Color: {proforma.color}")
                p.drawString(50, 700, f"Chapa: {proforma.chapa}")
                p.drawString(50, 640, f"Material: {proforma.material.material_name}")
                p.drawString(50, 680, f"Precio Instalación: {proforma.precioinstalacion}")
                p.drawString(50, 660, f"Precio Total: {proforma.preciototal}")
                p.showPage()
                p.save()

                buffer.seek(0)
                nombre_archivo = f'proforma_{proforma.proforma_num}.pdf'
                proforma.pdf.save(nombre_archivo, ContentFile(buffer.read()))
                buffer.close()
                proforma.save()

                cotizacion_seleccionada.estado = 'revisado'
                cotizacion_seleccionada.save()
                messages.success(request, 'Proforma guardada correctamente.')
                return redirect('bandeja_cotizaciones')
    contexto = {
        'cotizaciones': cotizaciones,
        'cotizacion_activa': cotizacion_seleccionada,
        'form': form, #ProformaForm(),  # nuevo formulario limpio
        'precio_calculado': precio_calculado,
        'proforma': proforma         # <-- PASA LA PROFORMA AL CONTEXTO
        }
    return render(request, 'proforma/bandeja.html', contexto)

def descargar_pdf(request, proforma_uid):
    proforma = Proforma.objects.get(uid=proforma_uid)

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica", 12)
    p.drawString(50, 800, f"Proforma N°: {proforma.proforma_num}")
    p.drawString(50, 780, f"Cliente: {proforma.cliente.username}")
    p.drawString(50, 760, f"Alto: {proforma.alto}")
    p.drawString(50, 740, f"Ancho: {proforma.ancho}")
    p.drawString(50, 720, f"Color: {proforma.color}")
    p.drawString(50, 700, f"Chapa: {proforma.chapa}")
    p.drawString(50, 680, f"Precio Instalación: {proforma.precioinstalacion}")
    p.drawString(50, 660, f"Precio Total: {proforma.preciototal}")
    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'proforma_{proforma.proforma_num}.pdf')

@login_required
def formulario_proforma(request):
    productos = ProductMaterial.objects.all()
    return render(request, 'product/proforma.html', {
        'productos': productos,
    })

@login_required
def guardar_proforma(request):
    if request.method == 'POST':
        numero = f"P{str(Proforma.objects.count() + 1).zfill(4)}"
        proforma = Proforma.objects.create(
            proforma_num=numero,
            cliente=request.user,
            preciototal=0,
            estado="pendiente",
            fecha=date.today()
        )

        cantidades = request.POST.getlist('cantidad[]')
        productos = request.POST.getlist('producto[]')  # uids de ProductMaterial
        altos = request.POST.getlist('alto[]')
        anchos = request.POST.getlist('ancho[]')
        colores = request.POST.getlist('color[]')
        instalaciones = request.POST.getlist('instalacion[]')
        preguntas1 = request.POST.getlist('pregunta1[]')
        preguntas2 = request.POST.getlist('pregunta2[]')
        preguntas3 = request.POST.getlist('pregunta3[]')

        total_general = 0

        for i in range(len(productos)):
            print("🔍 Valor recibido:", productos[i])

            try:
                producto = ProductMaterial.objects.get(uid=productos[i])
            except ProductMaterial.DoesNotExist:
                print(f"❌ No existe ProductMaterial con uid={productos[i]}")
                continue  # salta esa fila
            
            
            cantidad = float(cantidades[i]) if cantidades[i] else 1
            alto = float(altos[i]) if altos[i] else 0
            ancho = float(anchos[i]) if anchos[i] else 0
            color = colores[i]
            instalar = instalaciones[i] == 'on'
            p1, p2, p3 = preguntas1[i], preguntas2[i], preguntas3[i]

            precio = 100  # reemplazar luego con lógica real
            precio_instalacion = 50 if instalar else 0
            precio_total = (precio * cantidad) + precio_instalacion

            Cotizacion.objects.create(
                proforma=proforma,
                producto=producto,
                cantidad=cantidad,
                alto=alto,
                ancho=ancho,
                color=color,
                chapa="chapa: izquierda abre: afuera",
                pregunta_1=p1,
                pregunta_2=p2,
                pregunta_3=p3,
                precio=precio,
                precioinstalacion=precio_instalacion,
                preciototal=precio_total
            )

            total_general += precio_total

        proforma.preciototal = total_general
        proforma.slug = slugify(numero)
        proforma.save()

        if total_general == 0:
            proforma.delete()  # elimina la proforma vacía
            messages.warning(request, "No se pudo guardar ninguna cotización.")
            return redirect('formulario_proforma')

        return redirect('mis_proformas')



@login_required
def mis_proformas(request):
    proformas = Proforma.objects.filter(cliente=request.user).order_by('-fecha')
    return render(request, 'proforma/mis_proformas.html', {'proformas': proformas})