from csv import list_dialects
from django.contrib import admin

# Register your models here.

from .models import *

class ProductImageAdmin(admin.StackedInline):
    model =ProductImage

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name' , 'price' ]
    inlines = [ProductImageAdmin]

class ModeloImageAdmin(admin.StackedInline):
    model =ModeloImage

class ModeloAdmin(admin.ModelAdmin):
    list_display = ['modelo_name' , 'slug' ]
    inlines = [ModeloImageAdmin]

@admin.register(Acabado)
class Acabado(admin.ModelAdmin):
    list_display = ['acabado_name' , 'description']
    model = Acabado

@admin.register(Seguridad)
class Seguridad(admin.ModelAdmin):
    list_display = ['seguridad_name' , 'description']
    model = Seguridad
    
@admin.register(Estructura)
class Estructura(admin.ModelAdmin):
    list_display = ['estructura_name' , 'slug']
    model = Estructura

#@admin.register(SizeVariant)
#class SizeVariantAdmin(admin.ModelAdmin):
#    list_display = ['size_name' , 'price']
#
#    model = SizeVariant

admin.site.register(Category)

admin.site.register(Product ,ProductAdmin)
admin.site.register(Modelo ,ModeloAdmin)


admin.site.register(ProductImage)
admin.site.register(ModeloImage)
