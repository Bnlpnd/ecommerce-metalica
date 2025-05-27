from django.urls import path
from .views import *

urlpatterns = [
    path('galeria', galeria_view, name='galeria'),
    path('detalle/<uuid:uid>/', detalle_producto, name='detalle_producto'),
    
    # Vista principal de creación de proforma
    path('proforma/', proforma_view, name='proforma'),

    # Ajax para actualizar modelos según tipo
    path('ajax/modelos_por_tipo/', obtener_modelos_por_tipo, name='modelos_por_tipo'),
]
