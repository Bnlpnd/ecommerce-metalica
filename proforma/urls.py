from django.urls import path
from . import views

urlpatterns = [
    # Agrega una vista de prueba temporal
    path('ping/', views.ping, name='proforma_ping'),
    path('cotizar/<uuid:product_uid>/', views.solicitar_cotizacion, name='solicitar_cotizacion'),

]
