from django.urls import path
from .views import *

urlpatterns = [
    path('galeria', galeria_view, name='galeria')
]
