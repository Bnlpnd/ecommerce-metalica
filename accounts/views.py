from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login as auth_login, logout
from django.http import HttpResponseRedirect,HttpResponse
from django.core.paginator import Paginator
from django.db import models as django_models
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods 
from base.tokens import account_activation_token
from datetime import date, timedelta
from decimal import Decimal
from .models import Profile, Account
from .forms import ClienteProfileForm
from proforma.models import Proforma, Contrato
from base.emails  import send_account_activation_email, send_password_reset_email

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email).first()

        if not user_obj:
            messages.warning(request, 'Cuenta no encontrada.')
            return HttpResponseRedirect(request.path_info)

        if not user_obj.profile.is_email_verified:
            messages.warning(request, 'Tu cuenta no ha sido verificada.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email , password= password)
        if user_obj:
            auth_login(request , user_obj)
            return redirect('/')

        messages.warning(request, 'Credenciales incorrectas.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/login.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Debug: Print the received values
        print(f"First Name: {first_name}, Last Name: {last_name}, Email: {email}, Password: {password}")

        if not first_name or not last_name or not email or not password:
            messages.warning(request, 'Todos los campos son requeridos.')
            #return HttpResponseRedirect(request.path_info)
            return redirect('register')
        
        user_obj = User.objects.filter(username = email).first()

        if user_obj:
            messages.warning(request, 'El correo ya se encuentra registrado.')
            #return HttpResponseRedirect(request.path_info)
            return redirect('register')

        print(email)

        user_obj = User.objects.create_user(first_name = first_name , last_name= last_name , email = email , username = email)
        user_obj.set_password(password)
        user_obj.is_active = False 
        # Desactiva la cuenta hasta que se verifique el email
        user_obj.save()

        #mostrar que se guardo
        print(f"guardado {user_obj}")

        # Verifica si el usuario ya tiene un perfil
        profile = Profile.objects.filter(user=user_obj).first()
        if not profile:
            # Crea el perfil y genera el token de activación
            profile = Profile.objects.create(user=user_obj, email_token=account_activation_token.make_token(user_obj))
        else:
            profile.email_token = account_activation_token.make_token(user_obj)
            profile.save()
            
        print(f"Perfil creado: {profile}")

        # Verificación antes de enviar el correo
        if not isinstance(user_obj, User):
            raise ValueError("Expected a User object but got something else")
        
        send_account_activation_email(user_obj, profile.email_token)
        
        messages.success(request, 'Se ha enviado un correo electrónico a su correo. Por favor verifique su correo electrónico para completar el registro.')
        #return HttpResponseRedirect(request.path_info)
        return redirect('login')
        
    return render(request ,'accounts/register.html')

def activate_email(request , email_token):
    try:
        profile = Profile.objects.get(email_token= email_token)
        profile.is_email_verified = True
        profile.save()
        profile.user.is_active = True  # Activar la cuenta del usuario
        profile.user.save()
        messages.success(request, 'Tu correo fue verificado. Puedes Iniciar Sesión ahora!')
        return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, 'Invalid email token')
        return HttpResponse('Invalid Email token')
   
def logout_view(request):
    logout(request)
    return redirect('login')
    
def reset_password(request, email_token=None):
    if request.method == 'GET':
        try:
            profile = Profile.objects.get(email_token=email_token)
            request.session['uid'] = profile.user.id
            return render(request, 'accounts/reset_password.html')
        except Profile.DoesNotExist:
            messages.error(request, 'El enlace es inválido o ha expirado.')
            return redirect('forgot_password')

    elif request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        print(f"password: {password}")
        print(f"confirm_password: {confirm_password}")
        print(f"email_token: {email_token}")

        if password == confirm_password:
            uid = request.session.get('uid')
            print(f"uid - reset: {uid}")
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'La contraseña se actualizó correctamente')
            return redirect('login')
        else:
            messages.error(request, 'La contraseña de confirmación no concuerda')
            return redirect('reset_password')
    
    return render(request, 'accounts/reset_password.html', {
        'email_token': email_token
    })

@login_required(login_url='login_view')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()

                messages.success(request, 'La contraseña se actualizó correctamente')
                return redirect('change_password')
            else:
                messages.error(request, 'Los datos no son válidos, ingresa una contraseña correcta')
                return redirect('change_password')
        else:
            messages.error(request, 'La contraseña no coincide con la confirmación')
            return redirect('change_password')

    return render(request, 'accounts/change_password.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(username=email).first()

        if not user:
            messages.error(request, 'No existe una cuenta registrada con este correo.')
            return redirect('forgot_password')

        profile = Profile.objects.filter(user=user).first()
        if not profile:
            messages.error(request, 'No se encontró el perfil del usuario.')
            return redirect('forgot_password')

        # Generar nuevo token con el sistema existente
        token = account_activation_token.make_token(user)
        profile.email_token = token
        profile.save()

        # Enviar correo con enlace de recuperación
        send_password_reset_email(user, token)

        messages.success(request, 'Se ha enviado un correo con el enlace para restablecer tu contraseña.')
        return redirect('login')

    return render(request, 'accounts/forgot_password.html')
 
def get_cliente_dashboard_stats(user):
    return {
        'total_proformas': Proforma.objects.filter(cliente=user).count(),
        'total_contratos': Contrato.objects.filter(proforma__cliente=user).count(),
        'proformas_pendientes': Proforma.objects.filter(cliente=user, estado='pendiente').count(),
        'contratos_pendientes': Contrato.objects.filter(proforma__cliente=user, estado_pedido='pendiente').count(),
    }

@login_required
def dashboard_cliente(request):
    """Dashboard principal para clientes"""
    # Verificar que el usuario sea cliente
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'cliente':
        messages.warning(request, "Acceso denegado. Esta sección es solo para clientes.")
        return redirect('home')
    
    # Estadísticas básicas para mostrar en el dashboard
    stats = get_cliente_dashboard_stats(request.user)
    return render(request, 'accounts/dashboard_cliente.html', stats)

@login_required
@require_http_methods(["GET", "POST"])
def perfil_cliente(request):
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'cliente':
        messages.warning(request, "Acceso denegado. Esta sección es solo para clientes.")
        return redirect('home')

    profile = request.user.profile

    if request.method == 'POST':
        print("📨 POST AJAX recibido")
        form = ClienteProfileForm(request.POST, request.FILES, user=request.user, profile=profile)

        if form.is_valid():
            form.save(request.user, profile)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('accounts/perfil_cliente_fragment.html', {
                    'form': ClienteProfileForm(user=request.user, profile=profile),
                    'profile': profile
                }, request=request)
                return JsonResponse({'success': True, 'html': html})

            return redirect('perfil_cliente')

        else:
            errors = {field: error.get_json_data() for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors}, status=400)

    else:
        form = ClienteProfileForm(user=request.user, profile=profile)
        stats = get_cliente_dashboard_stats(request.user)
        return render(request, 'accounts/perfil_cliente.html', {'form': form, 'profile': profile, 'tab': 'perfil', **stats})

@login_required 
def mis_proformas_cliente(request):
    """Vista de proformas para clientes con filtros"""
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'cliente':
        messages.warning(request, "Acceso denegado. Esta sección es solo para clientes.")
        return redirect('home')
    
    # Filtros
    numero_proforma = request.GET.get('numero_proforma', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    
    # Query base filtrado por cliente
    proformas = Proforma.objects.filter(cliente=request.user).order_by('-fecha')
    
    # Aplicar filtros
    if numero_proforma:
        proformas = proformas.filter(proforma_num__icontains=numero_proforma)
    
    if estado_filtro and estado_filtro != 'todos':
        proformas = proformas.filter(estado=estado_filtro)
    
    # Paginación
    paginator = Paginator(proformas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    stats = get_cliente_dashboard_stats(request.user)

    context = {
        'proformas': page_obj,
        'numero_proforma': numero_proforma,
        'estado_filtro': estado_filtro,
        'total_proformas_filtered': proformas.count(),
        'tab': 'proformas',
         **stats,
    }
    
    return render(request, 'accounts/mis_proformas_cliente.html', context)

@login_required
def mis_contratos_cliente(request):
    """Vista de contratos para clientes con filtros"""
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'cliente':
        messages.warning(request, "Acceso denegado. Esta sección es solo para clientes.")
        return redirect('home')
    
    # Filtros
    numero_contrato = request.GET.get('numero_contrato', '').strip()
    numero_proforma = request.GET.get('numero_proforma', '').strip()
    estado_pedido = request.GET.get('estado_pedido', '').strip()
    estado_deuda = request.GET.get('estado_deuda', '').strip()
    
    # Query base filtrado por cliente
    contratos = Contrato.objects.filter(proforma__cliente=request.user).select_related('proforma').order_by('-fecha')
    
    # Aplicar filtros
    if numero_contrato:
        contratos = contratos.filter(contrato_num__icontains=numero_contrato)
        
    if numero_proforma:
        contratos = contratos.filter(proforma__proforma_num__icontains=numero_proforma)
    
    if estado_pedido and estado_pedido != 'todos':
        contratos = contratos.filter(estado_pedido=estado_pedido)
        
    if estado_deuda and estado_deuda != 'todos':
        if estado_deuda == 'debe':
            contratos = contratos.filter(acuenta__lt=django_models.F('preciototal'))
        elif estado_deuda == 'pagado':
            contratos = contratos.filter(acuenta__gte=django_models.F('preciototal'))
    
    # Paginación
    paginator = Paginator(contratos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    stats = get_cliente_dashboard_stats(request.user)
    
    context = {
        'contratos': page_obj,
        'numero_contrato': numero_contrato,
        'numero_proforma': numero_proforma,
        'estado_pedido': estado_pedido,
        'estado_deuda': estado_deuda,
        'total_contratos_filtered': contratos.count(),
        'tab': 'contratos',
         **stats,
    }
    
    return render(request, 'accounts/mis_contratos_cliente.html', context)

@login_required
def ver_contrato_cliente(request, contrato_num):
    """Vista de solo lectura del contrato para clientes"""
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'cliente':
        messages.warning(request, "Acceso denegado. Esta sección es solo para clientes.")
        return redirect('home')
    
    # Verificar que el contrato pertenezca al cliente
    contrato = get_object_or_404(Contrato, contrato_num=contrato_num, proforma__cliente=request.user)
    
    stats = get_cliente_dashboard_stats(request.user)
    
    context = {
        'contrato': contrato,
        'es_cliente': True,  # Flag para mostrar vista de solo lectura
        'tab': 'contratos',
         **stats,
    }
    
    return render(request, 'accounts/ver_contrato_cliente.html', context)

@login_required
def generar_contrato_cliente(request, proforma_num):
    """Generar contrato desde el dashboard del cliente"""
    if not hasattr(request.user, 'profile') or request.user.profile.rol != 'cliente':
        messages.warning(request, "Acceso denegado. Esta sección es solo para clientes.")
        return redirect('home')
    
    # Verificar que la proforma pertenezca al cliente
    proforma = get_object_or_404(Proforma, proforma_num=proforma_num, cliente=request.user)

    # Verificar si la proforma tiene menos de 20 días
    if (date.today() - proforma.fecha).days > 20:
        messages.warning(request, "La proforma ha vencido y no se puede generar un contrato.")
        return redirect('mis_proformas_cliente')

    cotizaciones = proforma.cotizaciones.prefetch_related('opciones').all()

    if request.method == 'POST':
        from proforma.models import OpcionCotizacion, OpcionContrato
        from proforma.utils.pdf_utils import render_to_pdf
        from django.core.files.base import ContentFile
        import uuid
        
        opcion_ids = []
        detalle_extra = request.POST.get('detalle_extra', '')

        for cotizacion in cotizaciones:
            opcion_id = request.POST.get(f"opcion_cotizacion_{cotizacion.id}")
            if not opcion_id:
                messages.error(request, f"Debe seleccionar una opción para el producto '{cotizacion.modelo.model_name}'.")
                return redirect('generar_contrato_cliente', proforma_num=proforma_num)
            opcion_ids.append(opcion_id)
            
        # Calcular total
        total = 0
        for opcion_id in opcion_ids:
            opcion = OpcionCotizacion.objects.get(id=opcion_id)
            total += float(opcion.preciototal)

        # Calcular 50% de abono
        acuenta = total * 0.5
        saldo = total - acuenta
        
        # Fecha de entrega: 7 días hábiles (aproximadamente 10 días calendario)
        fecha_entrega = date.today() + timedelta(days=10)

        contrato_num = f"C{str(uuid.uuid4())[:8].upper()}"
        contrato = Contrato.objects.create(
            contrato_num=contrato_num,
            cantidad=len(opcion_ids),
            preciototal=Decimal(str(total)),
            acuenta=Decimal("0.00"),  # 🔧 agrégalo explícitamente
            saldo=Decimal(str(total)),
            fechaEntrega=fecha_entrega,
            detale_extra=detalle_extra,
            proforma=proforma
        )

        # Relacionar opciones seleccionadas
        for opcion_id in opcion_ids:
            opcion = OpcionCotizacion.objects.get(id=opcion_id)
            OpcionContrato.objects.create(
                contrato=contrato,
                cotizacion=opcion.cotizacion,
                opcion=opcion
            )

        # Generar PDF del contrato
        context = {'contrato': contrato, 'opciones': contrato.opciones_elegidas.all(), 'abono_sugerido': acuenta }
        pdf_file = render_to_pdf('proforma/pdf_contrato.html', context)
        if pdf_file:
            contrato.pdf.save(f"{contrato.contrato_num}.pdf", ContentFile(pdf_file.read()))
            messages.success(request, f"Contrato {contrato_num} generado correctamente. Monto a abonar: S/. {acuenta:.2f}")
        else:
            messages.warning(request, "Contrato creado pero no se pudo generar el PDF.")

        return redirect('mis_contratos_cliente')

    # Calcular total para mostrar resumen
    total_estimado = 0
    for cotizacion in cotizaciones:
        if cotizacion.opciones.exists():
            # Tomar la primera opción como referencia para el cálculo
            total_estimado += float(cotizacion.opciones.first().preciototal or 0)
    
    stats = get_cliente_dashboard_stats(request.user)

    context = {
        'proforma': proforma,
        'cotizaciones': cotizaciones,
        'total_estimado': total_estimado,
        'abono_requerido': total_estimado * 0.5,
        'fecha_entrega_estimada': date.today() + timedelta(days=10),
        'tab': 'proformas',
        **stats
    }

    return render(request, 'accounts/generar_contrato_cliente.html', context)

