from django import forms
from .models import *
from products.models import Material

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['pregunta_1', 'pregunta_2', 'pregunta_3']
        widgets = {
            'pregunta_1': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control form-control-lg',
                'id': 'pregunta_1',
                'aria-label': 'Pregunta 1'
            }),
            'pregunta_2': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control form-control-lg',
                'id': 'pregunta_2',
                'aria-label': 'Pregunta 2'
            }),
            'pregunta_3': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control form-control-lg',
                'id': 'pregunta_3',
                'aria-label': 'Pregunta 3'
            }),
        }

class ProformaForm(forms.ModelForm):
    class Meta:
        model = Proforma
        fields = ['proforma_num', 'alto', 'ancho', 'color', 'chapa', 'detale_extra', 'material','precioinstalacion', 'precio', 'preciototal']
        widgets = {
            'proforma_num': forms.TextInput(attrs={ 'class': 'form-control' }),
            'alto': forms.NumberInput(attrs={ 'class': 'form-control' }),
            'ancho': forms.NumberInput(attrs={ 'class': 'form-control' }),
            'color': forms.Textarea(attrs={'rows': 3, 'style': 'height: 60px;', 'class': 'form-control'}),
            'chapa': forms.Textarea(attrs={'rows': 3, 'style': 'height: 60px;', 'class': 'form-control'}),
            'detale_extra': forms.Textarea(attrs={'rows': 3, 'style': 'height: 60px;', 'class': 'form-control'}),
            'material': forms.Select(attrs={'class': 'form-control'}),  # ✅ dinámico desde la base de datos
            'precioinstalacion': forms.NumberInput(attrs={ 'class': 'form-control' }),
            'precio': forms.NumberInput(attrs={ 'class': 'form-control' }),
            'preciototal': forms.NumberInput(attrs={ 'class': 'form-control' }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['precioinstalacion'].required = False
        self.fields['precio'].required = False
        self.fields['preciototal'].required = False
