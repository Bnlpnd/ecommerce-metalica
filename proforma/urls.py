from django.urls import path
from .views import *
from . import views

urlpatterns = [
    # Agrega una vista de prueba temporal
    path('ping/', views.ping, name='proforma_ping'),
    path('cotizar/<uuid:product_uid>/', views.solicitar_cotizacion, name='solicitar_cotizacion'),
    path('bandeja/', bandeja_cotizaciones, name='bandeja_cotizaciones'),
    path('bandeja/<int:cotizacion_id>/', bandeja_cotizaciones, name='bandeja_proformas'),
    path('descargar-pdf/<uuid:proforma_uid>/', views.descargar_pdf, name='descargar_pdf'),
    path('guardar-proforma/', guardar_proforma, name='guardar_proforma'),
    path('mis-proformas/', mis_proformas, name='mis_proformas'),
    path('proforma/formulario/', formulario_proforma, name='formulario_proforma'),

]