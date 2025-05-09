from django import forms
from .models import *

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['pregunta_1', 'pregunta_2', 'pregunta_3']
        widgets = {
            'pregunta_1': forms.Textarea(attrs={'rows': 2}),
            'pregunta_2': forms.Textarea(attrs={'rows': 2}),
            'pregunta_3': forms.Textarea(attrs={'rows': 2}),
        }

class ProformaForm(forms.ModelForm):
    class Meta:
        model = Proforma
        fields = ['proforma_num', 'alto', 'ancho', 'color', 'chapa', 'detale_extra', 'precioinstalacion', 'preciototal']
        widgets = {
            'color': forms.Textarea(attrs={'rows': 3, 'style': 'height: 60px;'}),
            'chapa': forms.Textarea(attrs={'rows': 3, 'style': 'height: 60px;'}),
            'detale_extra': forms.Textarea(attrs={'rows': 3, 'style': 'height: 60px;'}),
        }


#class CostoPredictionForm(forms.Form):
 #    categoria = forms.IntegerField(label='categoria')
 #   modelo  = forms.IntegerField(label='modelo')
 #    acabado = forms.IntegerField(label='acabado')
  #   seguridad = forms.IntegerField(label='seguridad')
   #  alto  = forms.IntegerField(label='alto')
    # ancho = forms.IntegerField(label='ancho')
    