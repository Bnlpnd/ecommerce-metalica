from django.urls import path
from .views import *
from . import views
from accounts.views import *

urlpatterns = [
    path('ping/', views.ping, name='proforma_ping'),
    path('cotizar/<uuid:product_uid>/', views.solicitar_cotizacion, name='solicitar_cotizacion'),
    path('descargar-pdf/<uuid:proforma_uid>/', views.descargar_pdf, name='descargar_pdf'),
    path('guardar-proforma/', guardar_proforma, name='guardar_proforma'),
    path('formulario/', formulario_proforma, name='formulario_proforma'),

    # Dashboard cliente
    path('dashboard/', views.dashboard_trabajador, name='dashboard_trabajador'),
    path('bandeja/', views.bandeja_trabajador, name='bandeja_trabajador'),
    path('bandeja/<str:proforma_num>/', views.bandeja_trabajador, name='bandeja_trabajador_con_id'),

    path('ver/<str:proforma_num>', views.ver_proforma, name='ver_proforma'),
    path('ver/<str:without_layout>/<str:proforma_num>', views.ver_proforma, name='ver_proforma'),
    path('guardar-opciones/', views.guardar_opciones_cotizacion, name='guardar_opciones_cotizacion'),
    path('predecir-precio/', views.predecir_precio, name='predecir_precio'),
    path('proforma/pdf/<str:proforma_num>/', views.generar_pdf_proforma, name='generar_pdf_proforma'),
    path('proforma/<str:proforma_num>/generar-contrato/', generar_contrato_cliente, name='generar_contrato'),
    path('estado-proformas/', views.estado_proformas, name='estado_proformas'),
    path('estado-contratos/', views.estado_contratos, name='estado_contratos'),
    path('contrato/<str:contrato_num>/', views.ver_contrato, name='ver_contrato'),
    path('contratos/anular/<str:contrato_num>/', views.anular_contrato_cliente, name='anular_contrato_cliente'),
    path('mis-proformas/', views.redireccionar_mis_proformas, name='mis_proformas'),

    path('exportar-cotizaciones/', views.exportar_cotizaciones_csv, name='exportar_cotizaciones'),

]