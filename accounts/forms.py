from django import forms
from django.contrib.auth.models import User
from .models import Profile


class ClienteProfileForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nombre'
        }),
        label='Nombre'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu apellido'
        }),
        label='Apellido'
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': True
        }),
        label='Email',
        help_text='El email no se puede modificar'
    )
    
    direccion = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu dirección completa'
        }),
        label='Dirección'
    )
    
    distrito = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu distrito'
        }),
        label='Distrito'
    )
    
    referencia = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Punto de referencia (opcional)'
        }),
        label='Referencia'
    )
    
    dni = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu DNI',
            'maxlength': '8'
        }),
        label='DNI'
    )
    
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='Imagen de Perfil'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            
        if profile:
            self.fields['direccion'].initial = profile.direccion
            self.fields['distrito'].initial = profile.distrito
            self.fields['referencia'].initial = profile.referencia
            self.fields['dni'].initial = profile.dni

    def save(self, user, profile):
        # Actualizar User
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        
        # Actualizar Profile
        profile.direccion = self.cleaned_data['direccion']
        profile.distrito = self.cleaned_data['distrito']
        profile.referencia = self.cleaned_data['referencia']
        profile.dni = self.cleaned_data['dni']
        
        # Manejar imagen de perfil
        if self.cleaned_data['profile_image']:
            profile.profile_image = self.cleaned_data['profile_image']
            
        profile.save()
        
        return profile