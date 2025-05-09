from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from products.models import Product, ProductMaterial
from django.contrib import messages
import joblib
import os
from django.http import HttpResponseForbidden
from django.http import FileResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import Proforma

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
    cotizacion_seleccionada = get_object_or_404(Cotizacion, id=cotizacion_id) if cotizacion_id else cotizaciones.first()

    form = ProformaForm()
    precio_calculado = None  # <- para mostrar en la plantilla
    proforma = None

    if request.method == 'POST':
        form = ProformaForm(request.POST)
        if form.is_valid():
            proforma = form.save(commit=False)
            proforma.cliente = cotizacion_seleccionada.cliente
            proforma.productmaterial = cotizacion_seleccionada.producto.productmaterial_set.first()

            # Cálculo con algoritmo (solo como guía)
            modelo_path = os.path.join('modelo', 'modelo_lineal.pkl')
            if os.path.exists(modelo_path):
                modelo = joblib.load(modelo_path)
                datos = [[proforma.alto, proforma.ancho]]
                prediccion = modelo.predict(datos)
                precio_calculado  = round(prediccion[0], 2)
            # No se guarda el precio calculado. El usuario verá el valor y pondrá el precio real manualmente.


            # Total
            proforma.preciototal = proforma.precio + proforma.precioinstalacion
            proforma.save()

            # Generar PDF y guardarlo en el campo
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

            nombre_archivo = f'proforma_{proforma.proforma_num}.pdf'
            proforma.pdf.save(nombre_archivo, ContentFile(buffer.read()))
            buffer.close()
            proforma.save()

            # Marcar cotización como revisada
            cotizacion_seleccionada.estado = 'revisado'
            cotizacion_seleccionada.save()

            messages.success(request, 'Proforma guardada correctamente.')

            return redirect('bandeja_cotizaciones')  # Redirecciona para limpiar el POST

    contexto = {
        'cotizaciones': cotizaciones,
        'cotizacion_activa': cotizacion_seleccionada,
        'form': ProformaForm(),  # nuevo formulario limpio
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
