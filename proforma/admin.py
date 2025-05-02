from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Visit)
class Visit(admin.ModelAdmin):
    list_display = ['name' , 'phone']
    model = Visit