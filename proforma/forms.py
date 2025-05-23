from django import forms
from .models import *
from products.models import Material

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['pregunta_1', 'pregunta_2', 'pregunta_3','alto','ancho','precio', 'color','chapa', 'cantidad','precioinstalacion', 'preciototal']
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
        fields = ['proforma_num', 'preciototal']
        widgets = {
            'proforma_num': forms.TextInput(attrs={ 'class': 'form-control' }),
            'preciototal': forms.NumberInput(attrs={ 'class': 'form-control' }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preciototal'].required = False
