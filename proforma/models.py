from django.db import models
from django.contrib.auth.models import User
from products.models import ProductMaterial, Product, Material
from base.models import BaseModel
from django.utils.text import slugify

#proforma 
class Proforma(BaseModel):
    proforma_num = models.CharField(max_length=100) #P0001
    estado = models.CharField(max_length=20, default='pendiente')  # pendiente, revisado, etc.
    fecha = models.DateField(auto_now_add=True)
    preciototal = models.DecimalField(max_digits=10, decimal_places=2, default=0) #se le suma si hay instalacion
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proformas') 
    pdf = models.FileField(upload_to='proformas_pdfs/', blank=True, null=True)
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.proforma_num)
        super(Proforma, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f'Proforma numero {self.proforma_num}'


class Cotizacion(models.Model):
    proforma = models.ForeignKey(Proforma, on_delete=models.CASCADE, related_name='cotizaciones')
    producto = models.ForeignKey(ProductMaterial, on_delete=models.CASCADE, related_name='cotizaciones')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    alto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ancho = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    color = models.TextField(max_length=250, default="negro")
    chapa = models.TextField(max_length=250, default="chapa: izquierda abre: afuera")
    pregunta_1 = models.TextField()
    pregunta_2 = models.TextField()
    pregunta_3 = models.TextField()
    #estado = models.CharField(max_length=20, default='pendiente')
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precioinstalacion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preciototal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Cotización agregada'
    

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


class OpcionCotizacion(models.Model):
    cotizacion = models.ForeignKey('Cotizacion', on_delete=models.CASCADE, related_name='opciones')
    titulo = models.CharField(max_length=100)  # Ej: "Básico", "Full", "Premium"
    precio_sin_instalacion = models.DecimalField(max_digits=10, decimal_places=2)
    precio_con_instalacion = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion_adicional = models.TextField(blank=True)  # por si deseas dar detalles
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} - {self.cotizacion}'
