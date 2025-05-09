from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'rol', 'dni', 'direccion', 'distrito', 'is_email_verified']
    search_fields = ['user__username', 'dni', 'direccion']
    list_filter = ['rol', 'distrito', 'is_email_verified']
