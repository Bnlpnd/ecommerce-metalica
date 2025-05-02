from django.db import models

# Create your models here.
class Visit(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    direccion = models.CharField(max_length=400)
    referencia = models.TextField(blank=True)
    message = models.TextField(blank=True) #agregar fechas y horas posibles

    
    def __str__(self) -> str:
        return self.name