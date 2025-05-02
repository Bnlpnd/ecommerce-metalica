#import imp
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User


def send_account_activation_email(user_obj, token):
    # Verificación antes de enviar el correo
    if not isinstance(user_obj, User):
        raise ValueError("Expected a User object but got something else")
    
    print(f"ingreso al send_account") 
    activation_link = settings.BASE_URL + reverse('activate', args=[token])
    subject = '¡Activa tu cuenta!'
    message = f'Hola,\nPor favor, haz click en el link para activar tu cuenta:\n{activation_link}\n\nMuchas gracias!,\nTu equipo de Santa Ana.'
    sender_email = settings.EMAIL_HOST_USER  # This should be your email
    print(f"antes de user_obj") 
    
    recipient_list = [user_obj.email]

    print(f"Sending email to {user_obj.email}") 

    send_mail(subject, message, sender_email, recipient_list)