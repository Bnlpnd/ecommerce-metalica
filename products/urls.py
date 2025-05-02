from django.urls import path
from products.views import get_product
from . import views

urlpatterns = [
   
    path('<slug>/' , get_product , name="get_product"),
    #path('cotizar/', views.cotizar, name="cotizar")
    
]
