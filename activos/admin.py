from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models
from .models import Activo

# 🔹 Lista de departamentos
DEPARTAMENTOS = [
    ('Fiscalización', 'Fiscalización'),
    ('Recaudación', 'Recaudación'),
    ('Inmuebles Urbanos', 'Inmuebles Urbanos'),
    ('Gerencia de Licores', 'Gerencia de Licores'),
    ('Gerencia General', 'Gerencia General'),
    ('Jurídica', 'Jurídica'),
    ('Administración y Finanzas', 'Administración y Finanzas'),
]

# 🔹 Asegurarnos de que el campo 'departamento' exista en el modelo User
if not hasattr(User, 'departamento'):
    User.add_to_class(
        'departamento',
        models.CharField(max_length=50, choices=DEPARTAMENTOS, null=True, blank=True)
    )

# 🔹 Personalizamos la vista del usuario en el admin
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('departamento',)}),
    )
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff', 'departamento'
    )
    list_filter = BaseUserAdmin.list_filter + ('departamento',)


# 🔹 Re-registrar el modelo User con nuestro admin personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# 🔹 Admin del modelo Activo
@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "serial",
        "descripcion",
        "condicion",
        "responsable",
        "departamento",
        "fecha_registro",
        "activo",
    )
    list_filter = ("departamento", "condicion", "activo")
    search_fields = ("codigo", "serial", "descripcion", "responsable")
