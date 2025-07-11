# Generated by Django 5.2.1 on 2025-06-05 14:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proforma', '0004_remove_cotizacion_estado'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpcionCotizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('precio_sin_instalacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_con_instalacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('descripcion_adicional', models.TextField(blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('cotizacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opciones', to='proforma.cotizacion')),
            ],
        ),
    ]
