from django.contrib import admin
from .models import *

# Register your models here.
    
# Proforma
@admin.register(Proforma)
class ProformaAdmin(admin.ModelAdmin):
    list_display = ['proforma_num', 'cliente', 'productmaterial', 'precio', 'precioinstalacion', 'preciototal', 'fecha']
    list_filter = ['fecha', 'cliente', 'productmaterial']
    search_fields = ['proforma_num', 'cliente__username']
    readonly_fields = ['fecha', 'slug']
    autocomplete_fields = ['cliente', 'productmaterial']

    fieldsets = (
        ('Datos del cliente y producto', {
            'fields': ('proforma_num', 'cliente', 'productmaterial')
        }),
        ('Medidas y características', {
            'fields': ('alto', 'ancho', 'color', 'chapa', 'detale_extra')
        }),
        ('Precios', {
            'fields': ('precio', 'precioinstalacion', 'preciototal')
        }),
        ('Archivo y seguimiento', {
            'fields': ('pdf', 'fecha', 'slug')
        }),
    )
    

# Contrato (relacionado a Proforma)
@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ['contrato_num', 'proforma', 'cantidad', 'preciototal', 'acuenta', 'saldo', 'fecha', 'fechaEntrega']
    list_filter = ['fecha', 'fechaEntrega']
    search_fields = ['contrato_num', 'proforma__proforma_num']
    readonly_fields = ['fecha', 'slug']
    autocomplete_fields = ['proforma']

    fieldsets = (
        ('Referencia de Proforma', {
            'fields': ('contrato_num', 'proforma')
        }),
        ('Detalle de pago', {
            'fields': ('cantidad', 'preciototal', 'acuenta', 'saldo')
        }),
        ('Fechas y comentarios', {
            'fields': ('fecha', 'fechaEntrega', 'detale_extra')
        }),
        ('Archivo final', {
            'fields': ('pdf', 'slug')
        }),
    )