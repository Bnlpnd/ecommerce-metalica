from django.db import models
from base.models import BaseModel
from django.utils.text import slugify

#Material simple - intermedio - resistente
class Material(BaseModel):
    material_name = models.CharField(max_length=100)
    description = models.TextField(max_length=250, default="")
    
    def __str__(self) -> str:
        return self.material_name
     
# Tipo (puerta interior, exterior, porton, etc)  
class Tipo(BaseModel):
    tipo_name = models.CharField(max_length=100)
    description = models.TextField(max_length=250, default="")

    def __str__(self) -> str:
        return self.tipo_name

# producto (de barras, 4 puertas, etc)
class Product(BaseModel):
    product_name = models.CharField(max_length=100)
    description = models.TextField(max_length=250, default="")
    detalle = models.TextField(max_length=250, default="Medidas: Tiempo de elaboración:")
    tipo = models.ForeignKey(Tipo ,  on_delete=models.CASCADE,related_name="tipos", null=True, blank=True)

    def save(self , *args , **kwargs):
        self.slug = slugify(self.product_name)
        super(Product ,self).save(*args , **kwargs)

    def __str__(self) -> str:
        return self.product_name
    
# ProductMaterial 
class ProductMaterial(BaseModel):
    productmaterial_name = models.CharField(max_length=100)
    description = models.TextField(max_length=950, default="") #se agrega el listado de materiales segun el producto que se selecciona
    product = models.ForeignKey(Product ,  on_delete=models.CASCADE,related_name="products", default="")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="materials")

    def save(self , *args , **kwargs):
        self.slug = slugify(self.productmaterial_name)
        super(ProductMaterial ,self).save(*args , **kwargs)
    
    def __str__(self):
        return self.productmaterial_name


class ProductImage(BaseModel):
    product = models.ForeignKey(ProductMaterial , on_delete=models.CASCADE , related_name="product_images")
    image =  models.ImageField(upload_to="product")
