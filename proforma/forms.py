from django import forms
from .models import Visit

class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['name', 'email', 'phone', 'direccion', 'referencia', 'message']
        
        
class CostoPredictionForm(forms.Form):
     categoria = forms.IntegerField(label='categoria')
     modelo  = forms.IntegerField(label='modelo')
     acabado = forms.IntegerField(label='acabado')
     seguridad = forms.IntegerField(label='seguridad')
     alto  = forms.IntegerField(label='alto')
     ancho = forms.IntegerField(label='ancho')
     