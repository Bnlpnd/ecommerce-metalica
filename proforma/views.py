from django.http import HttpResponse, HttpResponseForbidden, FileResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import OuterRef, Exists,Subquery
from django.db import models
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from decimal import Decimal
from datetime import datetime,timedelta, date
import pandas as pd
from .utils.pdf_utils import render_to_pdf
import joblib
import os
from io import BytesIO
import uuid
BASE_DIR = settings.BASE_DIR
from proforma.models import Contrato,Proforma,ContadorProforma,Product, ProductMaterial, Material
from .forms import *
from .models import *
import csv
from django.utils.dateparse import parse_date

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
        messages.warning(request, "Acceso denegado. Esta sección es solo para trabajadores.")
        return redirect('home')

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

def generar_numero_proforma_unico():
    contador, _ = ContadorProforma.objects.get_or_create(pk=1)

    while True:
        contador.ultimo_numero += 1
        numero = f"P{contador.ultimo_numero:04d}"
        if not Proforma.objects.filter(proforma_num=numero).exists():
            contador.save()
            return numero

@login_required
def redireccionar_mis_proformas(request):
    if hasattr(request.user, 'profile'):
        if request.user.profile.rol == 'cliente':
            return redirect('mis_proformas_cliente')
        elif request.user.profile.rol == 'trabajador':
            return redirect('estado_proformas')
    return HttpResponseForbidden("Acceso no permitido.")

@login_required
def guardar_proforma(request):
    if request.method == 'POST':
        numero = generar_numero_proforma_unico()
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
        cotizaciones_guardadas = 0
        
        for i in range(len(modelos)):
            print("🔍 Valor recibido:", modelos[i])
            
            # ✅ Validar que todos los campos estén presentes
            if not (modelos[i] and cantidades[i] and altos[i] and anchos[i] and colores[i] and preguntas1[i] and preguntas2[i] and preguntas3[i]):
                continue  # salta esta fila si hay algo vacío
            
            #Product
            try:
                modelo = ProductMaterial.objects.get(uid=modelos[i])
                print(f"Existe modelo")
            except ProductMaterial.DoesNotExist:
                print(f"No existe ProductMaterial con uid={modelos[i]}")
                continue  # salta esa fila
            

            cantidad = float(cantidades[i]) if cantidades[i] else 1
            alto = float(altos[i]) 
            ancho = float(anchos[i])
            color = colores[i] 
            p1, p2, p3 = preguntas1[i], preguntas2[i], preguntas3[i]

            precio = 0  # reemplazar luego con lógica real
            precio_instalacion = 0
            precio_total = 0

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
                precioinstalacion=0,
                preciototal=precio_total
            )

            total_general += precio_total*cantidad
            cotizaciones_guardadas += 1

        if cotizaciones_guardadas == 0:
            proforma.delete()
            messages.warning(request, "Debe completar todos los campos de al menos una fila para enviar la proforma.")
            return redirect('formulario_proforma')
        
        proforma.preciototal = total_general
        proforma.slug = slugify(numero)
        proforma.save()

        if cantidad == 0:
            proforma.delete()  # elimina la proforma vacía
            messages.warning(request, "No se pudo guardar ninguna cotización.")
            return redirect('formulario_proforma')

        messages.success(request, "Proforma creada exitosamente")
        return redireccionar_mis_proformas(request)

@login_required
def mis_proformas(request):
    contrato_subquery = Contrato.objects.filter(proforma=OuterRef('pk')).values('contrato_num')[:1]

    proformas = Proforma.objects.filter(cliente=request.user).annotate(
        tiene_contrato_anotado=Exists(Contrato.objects.filter(proforma=OuterRef('pk'))),
        contrato_num=Subquery(contrato_subquery)
    ).order_by('-fecha')

    
    return render(request, 'proforma/mis_proformas.html', {
        'proformas': proformas
    })
    
def get_trabajador_dashboard_stats(user):
    return {
        'total_proformas': Proforma.objects.count(),
        'total_contratos': Contrato.objects.count(),
        'proformas_pendientes': Proforma.objects.filter(estado='pendiente').count(),
        'contratos_pendientes': Contrato.objects.filter(estado_pedido='pendiente').count(),
    }

@login_required
def dashboard_trabajador(request):
    """Dashboard principal para clientes"""
    # Verificar que el usuario sea cliente
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'trabajador':
        messages.warning(request, "Acceso denegado. Esta sección es solo para trabajadores.")
        return redirect('home')
    
    # Estadísticas básicas para mostrar en el dashboard
    stats = get_trabajador_dashboard_stats(request.user)
    return render(request, 'accounts/dashboard_trabajador.html', stats)

@login_required
def bandeja_trabajador(request, proforma_num=None):
    proformas = Proforma.objects.filter(estado='pendiente').order_by('fecha')
    print("🧾 Proformas cargadas:", proformas)
    
    stats = get_trabajador_dashboard_stats(request.user)

    return render(request, 'proforma/bandeja.html', {'proformas': proformas,
        'proforma_seleccionada': proforma_num, 'tab': 'bandeja',**stats})

def ver_proforma(request, proforma_num, without_layout=None):
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

    view = 'proforma/ver_proforma.html'
    if without_layout:
        view = 'proforma/ver_proforma_bandeja.html'
    
    stats = get_trabajador_dashboard_stats(request.user)

    return render(request, view, {
        'proforma': proforma,
        'cotizaciones': cotizaciones,
        'materiales': materiales,
        'tab': 'proformas',
        **stats
    })


modelo_arbol = joblib.load(os.path.join(BASE_DIR, 'modelo_arbol.pkl'))
@login_required
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

            datos = pd.DataFrame([[producto_cod, material_cod, alto, ancho ]],
                                 columns=['producto', 'material','alto', 'ancho'])

            modelo_path = os.path.join(BASE_DIR, 'modelo_arbol.pkl')
            if os.path.exists(modelo_path):
                print("🧠 Cargando modelo de Machine Learning...")
                modelo = joblib.load(modelo_path)

                print("🧠 Modelo espera:", modelo.feature_names_in_)
                print("🧪 Columnas de entrada al modelo:", datos.columns.tolist())
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
                if pt > 0:
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
        
        # Si es AJAX, devolver JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Opciones guardadas correctamente',
                'precio_total_proforma': float(proforma.preciototal),
                'cotizacion_id': cotizacion.id,
            })

        messages.success(request, "Guardado correctamente")
        return redirect('ver_proforma', proforma.proforma_num)
    return redirect('home')
    
@login_required
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
        
        #####
        
        subject = f"Proforma {proforma.proforma_num} atendida"
        message = (
            f"Estimado/a {proforma.cliente.get_full_name()},\n\n"
            f"Su proforma número {proforma.proforma_num} ha sido atendida. "
            "Adjuntamos el documento PDF con el detalle de su proforma.\n\n"
            "Gracias por confiar en nosotros."
        )
        
        if proforma.cliente.email:
            recipient = [proforma.cliente.email]
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient,
                bcc=["zoila.benel@gmail.com"]  # copia oculta para ti
            )

            # Adjuntar el PDF generado
            if proforma.pdf:
                pdf_path = proforma.pdf.path  # Ruta completa del archivo en disco
                with open(pdf_path, 'rb') as f:
                    email.attach(f"{proforma.proforma_num}.pdf", f.read(), 'application/pdf')
            else:
                print("⚠️ No se encontró el archivo PDF para adjuntar.")

            try:
                email.send()
                print("📧 Correo enviado al cliente con la proforma adjunta.")

            except Exception as e:
                print(f"❌ Error enviando correo: {e}")
        else:
            print("⚠️ El cliente no tiene un correo electrónico registrado.")
            messages.warning(request, "Proforma generada, pero el cliente no tiene correo registrado.")

        print("\n" + "="*60)
        print("🎉 PROCESO DE GENERACIÓN PDF COMPLETADO")
        print(f"📄 Proforma {proforma.proforma_num} marcada como ATENDIDA")
        print("="*60)
        
        messages.success(request, f"Proforma {proforma.proforma_num} generada y enviada al correo del cliente.")
        return redirect('bandeja_trabajador')  # Bandeja se filtra automáticamente a pendientes
    else:
        print("❌ ERROR: No se pudo generar el archivo PDF")
        return HttpResponse("❌ Error generando PDF", status=500)
    

@login_required
def estado_proformas(request):
    # Verificar que el usuario sea trabajador
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'trabajador':
        messages.warning(request, "Acceso denegado. Esta sección es solo para trabajadores.")
        return redirect('home')
    
    # Obtener parámetros de filtrado
    nombre_cliente = request.GET.get('nombre_cliente', '').strip()
    numero_proforma = request.GET.get('numero_proforma', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    
    # Construir queryset base
    proformas = Proforma.objects.select_related('cliente').order_by('-fecha')
    
    # Aplicar filtros
    if nombre_cliente:
        proformas = proformas.filter(
            models.Q(cliente__first_name__icontains=nombre_cliente) |
            models.Q(cliente__last_name__icontains=nombre_cliente) |
            models.Q(cliente__username__icontains=nombre_cliente)
        )
    
    if numero_proforma:
        proformas = proformas.filter(proforma_num__icontains=numero_proforma)
    
    if estado_filtro and estado_filtro != 'todos':
        proformas = proformas.filter(estado=estado_filtro)
    
    # Paginación
    paginator = Paginator(proformas, 20)  # 20 proformas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    stats = get_trabajador_dashboard_stats(request.user)

    context = {
        'proformas': page_obj,
        'nombre_cliente': nombre_cliente,
        'numero_proforma': numero_proforma,
        'estado_filtro': estado_filtro,
        'total_proformas': proformas.count(), 
        'tab': 'proformas',
        **stats
    }
    
    return render(request, 'proforma/estado_proformas.html', context)

@login_required
def anular_contrato_cliente(request, contrato_num):
    # Primero obtenemos el contrato
    contrato = get_object_or_404(Contrato, contrato_num=contrato_num)

    # Validar que el contrato pertenece al cliente autenticado
    if contrato.proforma.cliente != request.user:
        return HttpResponseForbidden("No tienes permiso para anular este contrato.")

    # Si es POST, cambiar el estado
    if request.method == 'POST':
        contrato.estado_pedido = 'anulado'
        contrato.save()
        messages.success(request, "Contrato anulado correctamente.")
        return redirect('mis_contratos_cliente')

    # Puedes redirigir o mostrar una página de confirmación si deseas
    return redirect('mis_contratos_cliente')

@login_required
def estado_contratos(request):
    # Verificar que el usuario sea trabajador
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'trabajador':
        messages.warning(request, "Acceso denegado. Esta sección es solo para trabajadores.")
        return redirect('home')
    
    # Obtener parámetros de filtrado
    nombre_cliente = request.GET.get('nombre_cliente', '').strip()
    numero_contrato = request.GET.get('numero_contrato', '').strip()
    numero_proforma = request.GET.get('numero_proforma', '').strip()
    estado_pedido = request.GET.get('estado_pedido', '').strip()
    estado_deuda = request.GET.get('estado_deuda', '').strip()
    
    # Construir queryset base
    contratos = Contrato.objects.select_related('proforma__cliente').order_by('-fecha')
    
    # Aplicar filtros
    if nombre_cliente:
        contratos = contratos.filter(
            models.Q(proforma__cliente__first_name__icontains=nombre_cliente) |
            models.Q(proforma__cliente__last_name__icontains=nombre_cliente) |
            models.Q(proforma__cliente__username__icontains=nombre_cliente)
        )
    
    if numero_contrato:
        contratos = contratos.filter(contrato_num__icontains=numero_contrato)
        
    if numero_proforma:
        contratos = contratos.filter(proforma__proforma_num__icontains=numero_proforma)
    
    if estado_pedido and estado_pedido != 'todos':
        contratos = contratos.filter(estado_pedido=estado_pedido)
        
    if estado_deuda and estado_deuda != 'todos':
        if estado_deuda == 'debe':
            contratos = contratos.filter(acuenta__lt=models.F('preciototal'))
        elif estado_deuda == 'pagado':
            contratos = contratos.filter(acuenta__gte=models.F('preciototal'))
    
    # Paginación
    paginator = Paginator(contratos, 20)  # 20 contratos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    stats = get_trabajador_dashboard_stats(request.user)
    
    context = {
        'contratos': page_obj,
        'nombre_cliente': nombre_cliente,
        'numero_contrato': numero_contrato,
        'numero_proforma': numero_proforma,
        'estado_pedido': estado_pedido,
        'estado_deuda': estado_deuda,
        'total_contratos': contratos.count(),
        'tab': 'contratos',
        **stats
    }
    
    return render(request, 'proforma/estado_contratos.html', context)

@login_required
def ver_contrato(request, contrato_num):
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'trabajador':
        messages.warning(request, "Acceso denegado. Esta sección es solo para trabajadores.")
        return redirect('home')

    contrato = get_object_or_404(Contrato, contrato_num=contrato_num)
    
    # Guardar estado original
    estado_pedido_original = contrato.estado_pedido
    saldo_original = contrato.saldo  # importante

    if request.method == 'POST':
        try:
            nueva_fecha_entrega = request.POST.get('fechaEntrega')
            nuevo_abono = request.POST.get('acuenta')
            nuevo_estado_pedido = request.POST.get('estado_pedido')

            if nueva_fecha_entrega:
                contrato.fechaEntrega = datetime.strptime(nueva_fecha_entrega, '%Y-%m-%d').date()
            
            if nuevo_abono:
                abono_decimal = Decimal(nuevo_abono)
                contrato.acuenta += abono_decimal

            # Recalcular saldo
            contrato.saldo = contrato.preciototal - contrato.acuenta
            
            # Actualizar estado pedido
            if nuevo_estado_pedido:
                contrato.estado_pedido = nuevo_estado_pedido

            contrato.save()

            # Detectar si cambió el estado de deuda (debe vs pagado)
            estado_deuda_actual = contrato.estado_deuda
            estado_deuda_anterior = 'pagado' if saldo_original <= 0 else 'debe'

            if (estado_pedido_original != contrato.estado_pedido or
                estado_deuda_actual != estado_deuda_anterior):
                enviar_notificacion_contrato(contrato, True, True)

            messages.success(request, "Contrato actualizado correctamente.")
            return redirect('ver_contrato', contrato_num=contrato_num)

        except Exception as e:
            messages.error(request, f"Error al actualizar el contrato: {str(e)}")
    
    stats = get_trabajador_dashboard_stats(request.user)

    context = {
        'contrato': contrato,
        'opciones_estado': [
            ('pendiente', 'Pendiente'),
            ('en_produccion', 'En Producción'),
            ('entregado', 'Entregado')
        ],
        'tab': 'contratos',
        **stats,
    }
    return render(request, 'proforma/ver_contrato.html', context)

def enviar_notificacion_contrato(contrato, cambio_estado_pedido, cambio_estado_deuda):
    """Envía notificación por correo cuando cambia el estado del contrato"""
    try:
        from django.core.mail import EmailMessage
        
        cliente = contrato.cliente
        if not cliente or not cliente.email:
            print(f"⚠️ Cliente {cliente} no tiene correo registrado")
            return
        
        # Construir mensaje
        cambios = []
        if cambio_estado_pedido:
            cambios.append(f"Estado del pedido: {contrato.get_estado_pedido_display()}")
        if cambio_estado_deuda:
            cambios.append(f"Estado de deuda: {contrato.estado_deuda.title()}")
        
        subject = f"Actualización de contrato {contrato.contrato_num}"
        message = (
            f"Estimado/a {cliente.get_full_name()},\n\n"
            f"Le informamos que su contrato número {contrato.contrato_num} ha sido actualizado:\n\n"
            f"📋 Cambios realizados:\n"
        )
        
        for cambio in cambios:
            message += f"• {cambio}\n"
        
        message += (
            f"\n📊 Estado actual:\n"
            f"• Fecha de entrega: {contrato.fechaEntrega.strftime('%d/%m/%Y')}\n"
            f"• Monto total: S/.{contrato.preciototal}\n"
            f"• A cuenta: S/.{contrato.acuenta}\n"
            f"• Saldo pendiente: S/.{contrato.saldo}\n"
            f"• Estado del pedido: {contrato.get_estado_pedido_display()}\n"
            f"• Estado de deuda: {contrato.estado_deuda.title()}\n\n"
            f"Gracias por confiar en nosotros.\n"
        )
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[cliente.email],
            bcc=["zoila.benel@gmail.com"]
        )
        
        email.send()
        print(f"📧 Notificación enviada a {cliente.email} por cambios en contrato {contrato.contrato_num}")
        
    except Exception as e:
        print(f"❌ Error enviando notificación de contrato: {e}")



@login_required
def exportar_cotizaciones_csv(request):
    if request.method == 'POST':
        fecha_inicio = parse_date(request.POST.get('fecha_inicio'))
        fecha_fin = parse_date(request.POST.get('fecha_fin'))

        cotizaciones = Cotizacion.objects.filter(
            proforma__fecha__range=(fecha_inicio, fecha_fin)
        ).select_related('proforma', 'producto__product', 'producto__material').prefetch_related('opciones')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cotizaciones_exportadas.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Proforma', 'Producto', 'Material',
            'Alto', 'Ancho', 'Color',
            'Precio Predicho', 'Precio Real', 'Precio Total',
            'Título Opción', 'Fecha Opción'
        ])

        for cot in cotizaciones:
            for opcion in cot.opciones.all():
                writer.writerow([
                    cot.proforma.proforma_num,
                    cot.producto.product.product_name,
                    cot.producto.material.material_name,
                    cot.alto,
                    cot.ancho,
                    cot.color,
                    opcion.precio_prediccion,
                    opcion.precio_real,
                    opcion.titulo,
                    opcion.fecha_creacion.strftime('%Y-%m-%d'),
                ])
        return response

    return render(request, 'proforma/exportar_cotizaciones.html')