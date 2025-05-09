from django.contrib import admin
from .models import *

@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ['tipo_name', 'description']

class ProductImageInline(admin.StackedInline):
    model =ProductImage
    extra = 1 #muestra 1 formulario vacio adicional


# PRINCIPAL
# producto (de barras, 4 puertas, etc)
@admin.register(Product) 
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name' , 'tipo','description']
    list_filter = ['tipo']
    search_fields = ['product_name']
    inlines = [ProductImageInline]
    

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['material_name', 'description']

# PRINCIPAL
# producto_material (de barras y simple)
@admin.register(ProductMaterial)
class ProductMaterialAdmin(admin.ModelAdmin):
    list_display = ['productmaterial_name', 'product', 'descripcion_materiales']
    search_fields = ['productmaterial_name', 'product__product_name']

    def descripcion_materiales(self, obj):
        return obj.material.material_name

    descripcion_materiales.short_description = "Material"
