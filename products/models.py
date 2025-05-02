from django.db import models
from base.models import BaseModel
from django.utils.text import slugify

#acabado de puerta
class Acabado(BaseModel):
    acabado_name = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    
    def __str__(self) -> str:
        return self.acabado_name
    
# estructura metálica (puerta, ventana, etc)  
class Estructura(BaseModel):
    estructura_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True , null=True , blank=True)

    def __str__(self) -> str:
        return self.estructura_name
    
# nivel de seguridad (alto, medio, bajo)  
class Seguridad(BaseModel):
    seguridad_name = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    
    def __str__(self) -> str:
        return self.seguridad_name

# tipo de puerta (puerta interior, exterior, etc)
class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True , null=True , blank=True)
    descripcion = models.TextField(max_length=250, default="")
    estructura = models.ForeignKey(Estructura ,  on_delete=models.CASCADE,related_name="estructuras", default="")

    def save(self , *args , **kwargs):
        self.slug = slugify(self.category_name)
        super(Category ,self).save(*args , **kwargs)

    def __str__(self) -> str:
        return self.category_name
    
# modelo
class Modelo(BaseModel):
    modelo_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True , null=True , blank=True)
    descripcion = models.TextField(max_length=250, default="")
    category = models.ForeignKey(Category ,  on_delete=models.CASCADE,related_name="categorys", default="")

    def save(self , *args , **kwargs):
        self.slug = slugify(self.modelo_name)
        super(Modelo ,self).save(*args , **kwargs)

    def __str__(self) -> str:
        return self.modelo_name

class ModeloImage(BaseModel):
    modelo = models.ForeignKey(Modelo , on_delete=models.CASCADE , related_name="modelo_images")
    image =  models.ImageField(upload_to="modelo")

#modelo de puerta
class Product(BaseModel):
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True  , null=True , blank=True)
    modelo = models.ForeignKey(Modelo ,  on_delete=models.CASCADE,related_name="modelos", default="")
    alto = models.IntegerField()
    ancho = models.IntegerField()
    price = models.IntegerField()
    product_desription = models.TextField() #lado chapa, a donde abre, color
    acabado = models.ForeignKey(Acabado ,  on_delete=models.CASCADE,related_name="acabados", default="")
    seguridad = models.ForeignKey(Seguridad ,  on_delete=models.CASCADE,related_name="seguridades", default="")
            
    def save(self , *args , **kwargs):
        self.slug = slugify(self.product_name)
        super(Product ,self).save(*args , **kwargs)

    def __str__(self) -> str:
        return self.product_name

class ProductImage(BaseModel):
    product = models.ForeignKey(Product , on_delete=models.CASCADE , related_name="product_images")
    image =  models.ImageField(upload_to="product")