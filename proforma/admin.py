from django.contrib import admin
from .models import *

# Cotizacion inline.
class CotizacionInline(admin.TabularInline):
    model = Cotizacion
    extra = 1  # puedes mostrar más si quieres
# Proforma
@admin.register(Proforma)
class ProformaAdmin(admin.ModelAdmin):
    list_display = ['proforma_num', 'cliente', 'preciototal', 'fecha']
    list_filter = ['estado', 'fecha', 'cliente']
    search_fields = ['proforma_num', 'cliente__username']
    readonly_fields = ['fecha', 'slug']
    autocomplete_fields = ['cliente']

    inlines = [CotizacionInline]

    fieldsets = (
        ('Datos del cliente y producto', {
            'fields': ('proforma_num', 'cliente','preciototal')
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
    



@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ['producto', 'proforma','cantidad','alto','ancho','color','chapa', 'precio', 'estado', 'precioinstalacion','fecha_creacion', 'preciototal']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['producto__product_name']
    readonly_fields = ['fecha_creacion']

    fieldsets = (
        ('Información del cliente y producto', {
            'fields': ('producto','cantidad','alto','ancho','color','chapa','precio','precioinstalacion','preciototal')
        }),
        ('Preguntas del formulario', {
            'fields': ('pregunta_1', 'pregunta_2', 'pregunta_3')
        }),
        ('Seguimiento', {
            'fields': ('estado', 'fecha_creacion')
        }),
    )