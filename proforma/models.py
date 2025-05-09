from django.db import models
from django.contrib.auth.models import User

from products.models import ProductMaterial
from base.models import BaseModel
from django.utils.text import slugify


#proforma 
class Proforma(BaseModel):
    proforma_num = models.CharField(max_length=100) #P0001
    fecha = models.DateField(auto_now_add=True)
    alto = models.DecimalField(max_digits=10, decimal_places=2)
    ancho = models.DecimalField(max_digits=10, decimal_places=2)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.TextField(max_length=250, default="negro")
    chapa = models.TextField(max_length=250, default="chapa: izquierda   abre: afuera")
    detale_extra = models.TextField(max_length=500, default=" ")  #se añade fecha tentativa de entrega
    precioinstalacion = models.DecimalField (max_digits=10, decimal_places=2)
    preciototal = models.DecimalField(max_digits=10, decimal_places=2) #se le suma si hay instalacion
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proformas')
    productmaterial = models.ForeignKey(ProductMaterial ,  on_delete=models.CASCADE,related_name="proformas", null=True, blank=True)
    pdf = models.FileField(upload_to='proformas_pdfs/', blank=True, null=True)
            
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.proforma_num)
        super(Proforma, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f'Proforma numero {self.proforma_num}'

# contrato 
class Contrato(BaseModel):
    contrato_num = models.CharField(max_length=100) #C0001
    cantidad = models.PositiveIntegerField()
    preciototal = models.DecimalField(max_digits=10, decimal_places=2)
    acuenta = models.DecimalField(max_digits=10, decimal_places=2)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    fechaEntrega = models.DateField()
    detale_extra = models.TextField(max_length=250, default=" ") #se agrega algun detalle extra
    proforma = models.ForeignKey(Proforma ,  on_delete=models.CASCADE,related_name="proformas", blank=True, null=True)
    pdf = models.FileField(upload_to='contratos_pdfs/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.contrato_num)
        super(Contrato, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.contrato_num