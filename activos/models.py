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

# 🔹 Categorías y subcategorías
CATEGORIAS_PRINCIPALES = [
    ('', 'Seleccione una categoría'),
    ('equipo_informatico', 'Equipo Informático'),
    ('mueble', 'Mueble'),
    ('equipo_especializado', 'Equipo Especializado'),
    ('otro', 'Otro'),
]

SUBCATEGORIAS = [
    # Equipos Informáticos
    ('equipos informáticos','Equipos Informáticos'),
    ('pc_escritorio', 'PC de Escritorio'),
    ('laptop', 'Laptop'),
    ('tablet', 'Tablet'),
    ('servidor', 'Servidor'),
    ('impresora', 'Impresora'),
    ('monitor', 'Monitor'),
    ('teclado', 'Teclado'),
    ('mouse', 'Mouse'),
    # Muebles
    ('mueble','Mueble'),
    ('escritorio', 'Escritorio'),
    ('silla', 'Silla'),
    ('archivador', 'Archivador'),
    ('estanteria', 'Estantería'),
    ('mesa', 'Mesa'),
    # Equipos Especializados
    ('equipos especializados','Equipos Especializados'),
    ('scanner', 'Scanner'),
    ('proyector', 'Proyector'),
    ('telefono', 'Teléfono IP'),
    ('switch', 'Switch de Red'),
    ('router', 'Router'),
    # Otros
    ('otro equipo', 'Otro Equipo'),
    ('herramienta', 'Herramienta'),
    ('material', 'Material de Oficina'),
]


# 🔹 Modelo de Activos
class Activo(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    serial = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField()
    categoria_principal = models.CharField(
        max_length=50, 
        choices=CATEGORIAS_PRINCIPALES,
        default=''
    )
    subcategoria = models.CharField(
        max_length=50, 
        choices=SUBCATEGORIAS,
        blank=True
    )
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

    def save(self, *args, **kwargs):
        # 🔹 QUITAMOS la generación automática de código
        # El código ahora debe ser ingresado manualmente por el usuario
        super().save(*args, **kwargs)

# 🔹 Añadir el campo departamento directamente al modelo User
if not hasattr(User, 'departamento'):
    User.add_to_class(
        'departamento',
        models.CharField(max_length=50, choices=DEPARTAMENTOS, null=True, blank=True)
    )