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
    
    # Manejar limpieza de opciones
    limpiar_opciones_id = request.GET.get('limpiar_opciones')
    if limpiar_opciones_id:
        try:
            cotizacion = get_object_or_404(Cotizacion, id=limpiar_opciones_id, proforma=proforma)
            opciones_eliminadas = cotizacion.opciones.count()
            cotizacion.opciones.all().delete()
            messages.success(request, f"Se eliminaron {opciones_eliminadas} opciones de la cotización.")
            return redirect('ver_proforma', proforma_num=proforma_num)
        except:
            messages.error(request, "Error al eliminar las opciones.")
    
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

            print("\n" + "="*50)
            print("🤖 PREDICCIÓN DE PRECIO CON INTELIGENCIA ARTIFICIAL")
            print("="*50)
            print(f"📏 Dimensiones: {alto} x {ancho} cm")
            print(f"🏷️  Producto: {producto_nombre}")
            print(f"🔧 Material: {material_nombre}")
            
            #Clasificacion para el modelo de Machine Learning
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

            print(f"🔢 Codificación para modelo ML:")
            print(f"   - Producto: '{producto_nombre}' → {producto_cod}")
            print(f"   - Material: '{material_nombre}' → {material_cod}")

            datos = pd.DataFrame([[alto, ancho, producto_cod, material_cod]],
                                 columns=['alto', 'ancho', 'producto', 'material'])

            modelo_path = os.path.join(BASE_DIR, 'modelo_arbol.pkl')
            if os.path.exists(modelo_path):
                print("🧠 Cargando modelo de Machine Learning...")
                modelo = joblib.load(modelo_path)
                pred = modelo.predict(datos)[0]
                precio_predicho = round(pred, 2)
                print(f"💡 PREDICCIÓN COMPLETADA: S/.{precio_predicho}")
                print("="*50)
                return JsonResponse({'precio': precio_predicho})
            else:
                print("❌ ERROR: No se encontró el modelo de ML")
                return JsonResponse({'error': 'Modelo no encontrado'}, status=500)
        
        except Exception as e:
            print("❌ Error en predicción:", e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

from .models import Cotizacion, OpcionCotizacion

@login_required
def guardar_opciones_cotizacion(request):
    if request.method == 'POST':
        print("="*60)
        print("📋 INICIANDO PROCESO DE GUARDADO DE OPCIONES")
        print("="*60)
        
        cotizacion_id = request.POST.get("cotizacion_id")
        proforma_id = request.POST.get("proforma_id")
        
        if not cotizacion_id:
            messages.error(request, "Error: No se recibió ID de cotización")
            return redirect('home')
            
        cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
        proforma = cotizacion.proforma  # Usar la proforma de la cotización
        
        print(f"📍 Procesando cotización ID: {cotizacion_id} | Proforma: {proforma.proforma_num}")
        print(f"🏷️  Producto: {cotizacion.producto.product.product_name}")
        
        # Actualizar campo chapa de la cotización específica
        chapa_cotizacion = request.POST.get("chapa_cotizacion")
        if chapa_cotizacion is not None:  # Permite guardar string vacío
            print(f"🔑 Actualizando chapa de cotización: '{chapa_cotizacion}'")
            cotizacion.chapa = chapa_cotizacion
            cotizacion.save()
            print(f"✅ Chapa guardada exitosamente en cotización")
        
        # Obtener datos del formulario - intentar ambos formatos de nombres
        precios = request.POST.getlist('preciototal[]') or request.POST.getlist('preciototal')
        titulos = request.POST.getlist('titulo[]') or request.POST.getlist('titulo') 
        materiales = request.POST.getlist('material_id[]') or request.POST.getlist('material_id')
        precios_real = request.POST.getlist('precio_real[]') or request.POST.getlist('precio_real')
        precios_predicho = request.POST.getlist('precio_predicho[]') or request.POST.getlist('precio_predicho')
        precios_instalacion = request.POST.getlist('precioinstalacion[]') or request.POST.getlist('precioinstalacion')
        descripciones = request.POST.getlist('descripcion_adicional[]') or request.POST.getlist('descripcion_adicional')
        
        print(f"📝 Datos recibidos del formulario:")
        print(f"   - Títulos: {[t for t in titulos if t]}")
        print(f"   - Precios reales: {[p for p in precios_real if p]}")
        print(f"   - Precios instalación: {[p for p in precios_instalacion if p]}")
        print(f"   - Precios totales: {[p for p in precios if p]}")

        # Limpiar opciones anteriores de esta cotización
        opciones_anteriores = OpcionCotizacion.objects.filter(cotizacion=cotizacion).count()
        if opciones_anteriores > 0:
            print(f"🧹 Eliminando {opciones_anteriores} opciones anteriores de la cotización")
        OpcionCotizacion.objects.filter(cotizacion=cotizacion).delete()

        print("\n" + "="*40)
        print("💾 PROCESANDO OPCIONES DE COTIZACIÓN")
        print("="*40)
        
        # Guarda todas las opciones que tengan datos válidos
        opciones_guardadas = 0
        total_campos = max(len(precios), len(titulos), len(precios_real), len(precios_instalacion), len(precios_predicho), len(descripciones))
        
        primera_opcion_datos = None  # Para guardar los datos de la primera opción válida
        
        for i in range(total_campos):
            try:
                # Obtener valores con validación de índices
                titulo = titulos[i].strip() if i < len(titulos) and titulos[i] else ""
                pt = float(precios[i]) if i < len(precios) and precios[i] else 0
                pr = float(precios_real[i]) if i < len(precios_real) and precios_real[i] else 0
                pi = float(precios_instalacion[i]) if i < len(precios_instalacion) and precios_instalacion[i] else 0
                descripcion = descripciones[i].strip() if i < len(descripciones) and descripciones[i] else ""
                
                # Solo guarda si tiene al menos título o algún precio
                if titulo or pt > 0 or pr > 0 or pi > 0 or descripcion:
                    # Obtener y limpiar precio predicho
                    precio_pred = 0
                    if i < len(precios_predicho) and precios_predicho[i]:
                        precio_pred_str = precios_predicho[i]
                        # Limpiar el precio predicho de formato
                        precio_pred_str = precio_pred_str.replace("S/.", "").replace(",", "").strip()
                        try:
                            precio_pred = float(precio_pred_str)
                        except ValueError:
                            precio_pred = 0
                    
                    print(f"➕ Creando opción {opciones_guardadas + 1}: '{titulo or f'Opción {i+1}'}'")
                    print(f"   💰 Precio real: S/.{pr} | Instalación: S/.{pi} | Total: S/.{pt}")
                    
                    nueva_opcion = OpcionCotizacion.objects.create(
                        cotizacion=cotizacion,
                        titulo=titulo or f"Opción {i+1}",
                        precio_instalacion=pi,
                        descripcion_adicional=descripcion,
                        preciototal=pt,
                        precio_prediccion=precio_pred,
                        precio_real=pr
                    )
                    
                    opciones_guardadas += 1
                    
                    # Guardar datos de la primera opción válida para actualizar la cotización
                    if primera_opcion_datos is None:
                        primera_opcion_datos = {
                            'precio': pr,  # precio real va a campo precio
                            'precioinstalacion': pi,
                            'preciototal': pt
                        }
                        print(f"⭐ PRIMERA OPCIÓN seleccionada para actualizar cotización")
                    
            except (ValueError, IndexError) as e:
                continue
        
        print(f"✅ Total de opciones guardadas: {opciones_guardadas}")

        print("\n" + "="*40)
        print("🔄 ACTUALIZANDO DATOS DE COTIZACIÓN")
        print("="*40)
        
        # Actualizar la cotización con los valores de la primera opción
        if primera_opcion_datos:
            print(f"📊 Aplicando datos de primera opción a cotización:")
            print(f"   - Precio base: S/.{primera_opcion_datos['precio']}")
            print(f"   - Precio instalación: S/.{primera_opcion_datos['precioinstalacion']}")
            print(f"   - Precio total: S/.{primera_opcion_datos['preciototal']}")
            
            cotizacion.precio = primera_opcion_datos['precio']
            cotizacion.precioinstalacion = primera_opcion_datos['precioinstalacion']
            cotizacion.preciototal = primera_opcion_datos['preciototal']
            cotizacion.save()
            print(f"✅ Cotización actualizada exitosamente")
        else:
            print("⚠️  No se encontró primera opción válida para actualizar cotización")

        print("\n" + "="*40)
        print("🧮 RECALCULANDO TOTAL DE PROFORMA")
        print("="*40)
        
        # Recalcular total general de la proforma sumando las cotizaciones (no las opciones)
        total_general = 0
        cotizaciones_con_precio = 0
        
        for cot in proforma.cotizaciones.all():
            if cot.preciototal:
                total_general += cot.preciototal
                cotizaciones_con_precio += 1
                print(f"   + Cotización {cot.id} ({cot.producto.product.product_name}): S/.{cot.preciototal}")

        print(f"📊 RESUMEN DE CÁLCULO:")
        print(f"   - Cotizaciones con precio: {cotizaciones_con_precio}")
        print(f"   - Total general de proforma: S/.{total_general}")

        # Actualizar proforma
        proforma.preciototal = total_general
        proforma.save()
        print(f"✅ Proforma {proforma.proforma_num} actualizada con precio total: S/.{total_general}")
        
        print("\n" + "="*60)
        print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
        print("="*60)
        
        messages.success(request, "Guardado correctamente")
        return redirect('ver_proforma', proforma_num=proforma.proforma_num)

    return redirect('home')
    


@csrf_exempt
def generar_pdf_proforma(request, proforma_num):
    print("\n" + "="*60)
    print("📄 INICIANDO GENERACIÓN DE PDF FINAL")
    print("="*60)
    
    proforma = get_object_or_404(Proforma, proforma_num=proforma_num)
    cotizaciones = proforma.cotizaciones.prefetch_related('opciones').all()
    
    print(f"📋 Generando PDF para proforma: {proforma.proforma_num}")
    print(f"👤 Cliente: {proforma.cliente.get_full_name()}")
    print(f"💰 Precio total de proforma: S/.{proforma.preciototal}")
    print(f"📦 Cotizaciones incluidas: {cotizaciones.count()}")

    # Si es POST, actualizar datos de chapa antes de generar PDF
    if request.method == 'POST':
        print("\n🔄 Actualizando chapas finales antes de generar PDF...")
        # Actualizar chapa de cada cotización
        for cotizacion in cotizaciones:
            chapa_key = f'chapa_{cotizacion.id}'
            if chapa_key in request.POST:
                cotizacion.chapa = request.POST[chapa_key]
                cotizacion.save()
                print(f"   🔑 Chapa actualizada para cotización {cotizacion.id}: '{cotizacion.chapa}'")

    # Mostrar resumen de contenido del PDF
    print("\n📊 CONTENIDO DEL PDF:")
    for i, cotizacion in enumerate(cotizaciones, 1):
        print(f"   {i}. {cotizacion.producto.product.product_name}")
        print(f"      💰 Precio cotización: S/.{cotizacion.preciototal}")
        print(f"      🔑 Chapa: {cotizacion.chapa}")
        opciones_count = cotizacion.opciones.count()
        print(f"      📋 Opciones disponibles: {opciones_count}")

    context = {
        'proforma': proforma,
        'cotizaciones': cotizaciones
    }

    print("\n🔄 Generando archivo PDF...")
    pdf_file = render_to_pdf("proforma/pdf_proforma.html", context)
    
    if pdf_file:
        print("✅ PDF generado exitosamente")
        proforma.pdf.save(f"{proforma.proforma_num}.pdf", pdf_file)
        print(f"💾 Archivo guardado: {proforma.proforma_num}.pdf")
        
        print(f"🔄 Cambiando estado de proforma de '{proforma.estado}' a 'atendido'")
        proforma.estado = "atendido"
        proforma.save()
        
        print("\n" + "="*60)
        print("🎉 PROCESO DE GENERACIÓN PDF COMPLETADO")
        print(f"📄 Proforma {proforma.proforma_num} marcada como ATENDIDA")
        print("="*60)
        
        messages.success(request, "Generado correctamente")
        return redirect('bandeja_trabajador')  # Bandeja se filtra automáticamente a pendientes
    else:
        print("❌ ERROR: No se pudo generar el archivo PDF")
        return HttpResponse("❌ Error generando PDF", status=500)
    
    