from cmath import log
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login as auth_login, logout
from django.http import HttpResponseRedirect,HttpResponse
# Create your views here.
from .models import Profile, Account
from base.emails  import send_account_activation_email, send_password_reset_email
from base.tokens import account_activation_token


def login_view(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email).first()

        if not user_obj:
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)

        if not user_obj.profile.is_email_verified:
            messages.warning(request, 'Your account is not verified.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email , password= password)
        if user_obj:
            auth_login(request , user_obj)
            return redirect('/')

        messages.warning(request, 'Invalid credentials')
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

