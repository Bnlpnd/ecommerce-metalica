from django.http import HttpResponse, HttpResponseForbidden, FileResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from products.models import Product, ProductMaterial, Material
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
from django.views.decorators.csrf import csrf_exempt #no valida el token para hacer pruebas
from django.urls import reverse
from django.template.loader import render_to_string,  get_template
from .utils.pdf_utils import render_to_pdf
import tempfile
from django.http import HttpResponse
from xhtml2pdf import pisa


modelo_arbol = joblib.load(os.path.join(BASE_DIR, 'modelo_arbol.pkl'))

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

    proformas = Proforma.objects.filter(estado='pendiente').order_by('-fecha')
    
    # VERIFICAR SI HAY COTIZACIONES DISPONIBLES
    if not proformas.exists():
        messages.warning(request, "No hay proformas pendientes.")
        return render(request, 'proforma/bandeja.html', {
            'cotizaciones': [],
            'cotizacion_activa': None,
            'form': None,
            'precio_calculado': None,
            'proforma': None
        })
        
    return render(request, 'proforma/bandeja.html', {'proformas': proformas})


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
        'productos': productos})

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
        modelos = request.POST.getlist('modelo[]')  # uids de ProductMaterial
        altos = request.POST.getlist('alto[]')
        anchos = request.POST.getlist('ancho[]')
        colores = request.POST.getlist('color[]')
        preguntas1 = request.POST.getlist('pregunta1[]')
        preguntas2 = request.POST.getlist('pregunta2[]')
        preguntas3 = request.POST.getlist('pregunta3[]')

        total_general = 0

        for i in range(len(modelos)):
            print("🔍 Valor recibido:", modelos[i])

            #Product
            try:
                modelo = ProductMaterial.objects.get(uid=modelos[i])
                print(f"Existe modelo")
            except ProductMaterial.DoesNotExist:
                print(f"No existe ProductMaterial con uid={modelos[i]}")
                continue  # salta esa fila
            

            cantidad = float(cantidades[i]) if cantidades[i] else 1
            alto = float(altos[i]) if altos[i] else 0
            ancho = float(anchos[i]) if anchos[i] else 0
            color = colores[i]
            instalar = False
            p1, p2, p3 = preguntas1[i], preguntas2[i], preguntas3[i]

            precio = 0  # reemplazar luego con lógica real
            precio_instalacion = 50 if instalar else 0
            precio_total = (precio * cantidad) + precio_instalacion

            Cotizacion.objects.create(
                proforma=proforma,
                producto=modelo,
                cantidad=cantidad,
                alto=alto,
                ancho=ancho,
                color=color,
                chapa="chapa: izquierda abre: afuera",
                pregunta_1=p1,
                pregunta_2=p2,
                pregunta_3=p3,
                precio=precio,
                precioinstalacion=50 if instalar else 0,
                preciototal=precio_total
            )

            total_general += precio_total

        proforma.preciototal = total_general
        proforma.slug = slugify(numero)
        proforma.save()

        if cantidad == 0:
            proforma.delete()  # elimina la proforma vacía
            messages.warning(request, "No se pudo guardar ninguna cotización.")
            return redirect('formulario_proforma')

        return redirect('mis_proformas')

@login_required
def mis_proformas(request):
    proformas = Proforma.objects.filter(cliente=request.user).order_by('-fecha')
    return render(request, 'proforma/mis_proformas.html', {'proformas': proformas})

@login_required
def bandeja_trabajador(request, proforma_num=None):
    proformas = Proforma.objects.filter(estado='pendiente').order_by('fecha')
    print("🧾 Proformas cargadas:", proformas)
    return render(request, 'proforma/bandeja.html', {'proformas': proformas,
        'proforma_seleccionada': proforma_num})

@login_required
def ver_proforma(request, proforma_num):
    proforma = get_object_or_404(Proforma, proforma_num=proforma_num)
    cotizaciones = Cotizacion.objects.filter(proforma=proforma)
    materiales = Material.objects.all()
    
    return render(request, 'proforma/ver_proforma.html', {
        'proforma': proforma,
        'cotizaciones': cotizaciones,
        'materiales': materiales
    })

@csrf_exempt
def predecir_precio(request):
    if request.method == 'POST':
        try:
            alto = int(float(request.POST.get('alto', '0').replace(',', '.')))
            ancho = int(float(request.POST.get('ancho', '0').replace(',', '.')))
            material_nombre = request.POST.get('material_nombre')
            producto_nombre = request.POST.get('producto_nombre')

            print("Recibido en backend:")
            print("Alto:", alto)
            print("Ancho:", ancho)
            print("Producto nombre:", producto_nombre)
            print("Material nombre:", material_nombre)
            
            #Clasificacion
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
            
            producto_cod = codigos_producto.get(producto_nombre, 0)
            material_cod = codigos_material.get(material_nombre, 0)

            datos = pd.DataFrame([[alto, ancho, producto_cod, material_cod]],
                                 columns=['alto', 'ancho', 'producto', 'material'])

            print(f"🔢 Codificados: Producto {producto_cod}, Material {material_cod}")


            modelo_path = os.path.join(BASE_DIR, 'modelo_arbol.pkl')
            if os.path.exists(modelo_path):
                modelo = joblib.load(modelo_path)
                pred = modelo.predict(datos)[0]
                return JsonResponse({'precio': round(pred, 2)})
            else:
                print("❌ No se encontró el modelo.")
                return JsonResponse({'error': 'Modelo no encontrado'}, status=500)
        
        except Exception as e:
            print("❌ Error en predicción:", e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

from .models import Cotizacion, OpcionCotizacion

@login_required
def guardar_opciones_cotizacion(request):
    if request.method == 'POST':
        proforma_id = request.POST.get("proforma_id")
        proforma = get_object_or_404(Proforma, id=proforma_id)
        cotizaciones = Cotizacion.objects.filter(proforma=proforma)
        
        total_general = 0
        for c in cotizaciones:
            precios = request.POST.getlist('preciototal[]')
            titulos = request.POST.getlist('titulo[]')
            materiales = request.POST.getlist('material_id[]')
            descripciones = request.POST.getlist('descripcion_adicional[]')
            precios_real = request.POST.getlist('precio_real[]')
            precios_predicho = request.POST.getlist('precio_predicho[]')
            precios_instalacion = request.POST.getlist('precioinstalacion[]')

            # Solo guarda si hay precio total (primera opción)
            for i in range(3):
                try:
                    pt = float(precios[i])
                except:
                    pt = 0
                if pt > 0:
                    opcion = OpcionCotizacion.objects.create(
                        cotizacion=c,
                        titulo=titulos[i],
                        precio_instalacion=precios_instalacion[i],
                        descripcion_adicional=descripciones[i],
                        preciototal=pt,
                        precio_prediccion=precios_predicho[i].replace("S/.", "").strip(),
                        precio_real=precios_real[i]
                    )
                    # Suma solo la primera opción válida
                    if i == 0:
                        total_general += pt
                    break  # Solo guarda la primera opción válida

        # Marcar como atendido y guardar total
        proforma.estado = "atendido"
        proforma.preciototal = total_general

        # GENERAR PDF
        context = {
            'proforma': proforma,
            'cotizaciones': cotizaciones,
        }
        html_pdf = render_to_string("proforma_pdf.html", context)
        pdf_file = render_to_pdf(html_pdf)  # esto devuelve un ContentFile

        if pdf_file:
            proforma.pdf.save(f"{proforma.proforma_num}.pdf", pdf_file)

        proforma.save()
        messages.success(request, "Proforma procesada correctamente.")
        return redirect('bandeja_cotizaciones')  # cambia por tu URL final

    return redirect('home')
    


@csrf_exempt
def generar_pdf_proforma(request, proforma_num):
    proforma = get_object_or_404(Proforma, proforma_num=proforma_num)
    cotizaciones = proforma.cotizaciones.prefetch_related('opciones').all()

    context = {
        'proforma': proforma,
        'cotizaciones': cotizaciones
    }

    pdf_file = render_to_pdf("proforma/pdf_proforma.html", context)
    
    if pdf_file:
        proforma.pdf.save(f"{proforma.proforma_num}.pdf", pdf_file)
        proforma.estado = "atendido"
        proforma.save()
        return redirect('bandeja_trabajador')  # redirige a donde desees
    else:
        return HttpResponse("❌ Error generando PDF", status=500)
    
    