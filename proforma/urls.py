from django.urls import path
from .views import *
from . import views

urlpatterns = [
    # Agrega una vista de prueba temporal
    path('ping/', views.ping, name='proforma_ping'),
    path('cotizar/<uuid:product_uid>/', views.solicitar_cotizacion, name='solicitar_cotizacion'),
    #path('bandeja/', bandeja_cotizaciones, name='bandeja_cotizaciones'),
    #path('bandeja/<int:cotizacion_id>/', bandeja_cotizaciones, name='bandeja_proformas'),
    path('descargar-pdf/<uuid:proforma_uid>/', views.descargar_pdf, name='descargar_pdf'),
    path('guardar-proforma/', guardar_proforma, name='guardar_proforma'),
    path('mis-proformas/', mis_proformas, name='mis_proformas'),
    path('formulario/', formulario_proforma, name='formulario_proforma'),

    path('bandeja/', views.bandeja_trabajador, name='bandeja_trabajador'),
    path('bandeja/<str:proforma_num>/', views.bandeja_trabajador, name='bandeja_trabajador_con_id'),

    path('ver/<str:proforma_num>/', views.ver_proforma, name='ver_proforma'),
    path('guardar-opciones/', views.guardar_opciones_cotizacion, name='guardar_opciones_cotizacion'),
    path('predecir-precio/', views.predecir_precio, name='predecir_precio'),
    path('proforma/pdf/<str:proforma_num>/', views.generar_pdf_proforma, name='generar_pdf_proforma'),

]