from django.db import models
from django.contrib.auth.models import User

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


# 🔹 Modelo de Activos
class Activo(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    serial = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField()
    condicion = models.CharField(
        max_length=20,
        choices=[
            ('operativo', 'Operativo'),
            ('dañado', 'Dañado'),
        ],
        default='operativo'
    )
    responsable = models.CharField(max_length=100)
    departamento = models.CharField(max_length=50, choices=DEPARTAMENTOS)
    fecha_registro = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


# 🔹 Añadir el campo departamento directamente al modelo User
#    Esto te permite asignar un departamento a cada usuario desde /admin/auth/user/
if not hasattr(User, 'departamento'):
    User.add_to_class(
        'departamento',
        models.CharField(max_length=50, choices=DEPARTAMENTOS, null=True, blank=True)
    )
