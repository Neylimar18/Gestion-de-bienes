from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# 🔹 Lista de departamentos
DEPARTAMENTOS = [
    ('Fiscalización', 'Fiscalización'),
    ('Recaudación', 'Recaudación'),
    ('Inmuebles Urbanos', 'Inmuebles Urbanos'),
    ('Gerencia de Licores', 'Gerencia de Licores'),
    ('Gerencia General', 'Gerencia General'),
    ('Jurídica', 'Jurídica'),
    ('Administración y Finanzas', 'Administración y Finanzas'),
    ('Informática', 'Informática'),
    ('Calidad de Gestion', 'Calidad de Gestion'),
    ('GADT', 'GADT'),

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
    ('pc_escritorio', 'PC de Escritorio'),
    ('laptop', 'Laptop'),
    ('tablet', 'Tablet'),
    ('servidor', 'Servidor'),
    ('impresora', 'Impresora'),
    ('monitor', 'Monitor'),
    ('teclado', 'Teclado'),
    ('mouse', 'Mouse'),
    # Muebles
    ('escritorio', 'Escritorio'),
    ('silla', 'Silla'),
    ('archivador', 'Archivador'),
    ('estanteria', 'Estantería'),
    ('mesa', 'Mesa'),
    # Equipos Especializados
    ('scanner', 'Scanner'),
    ('proyector', 'Proyector'),
    ('telefono', 'Teléfono IP'),
    ('switch', 'Switch de Red'),
    ('router', 'Router'),
    # Otros
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


    departamento_anterior = models.CharField(max_length=100, blank=True, null=True)

    transferido_por = models.CharField(max_length=100, blank=True, null=True)
    recibido_por = models.CharField(max_length=100, blank=True, null=True)
    cargo_entrega = models.CharField(max_length=100, blank=True, null=True)
    cargo_recibe = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

    def save(self, *args, **kwargs):
       
        # El código ahora debe ser ingresado manualmente por el usuario
        super().save(*args, **kwargs)

# 🔹 Añadir el campo departamento directamente al modelo User
if not hasattr(User, 'departamento'):
    User.add_to_class(
        'departamento',
        models.CharField(max_length=50, choices=DEPARTAMENTOS, null=True, blank=True)
    )

# models.py
class TransferenciaActivo(models.Model):
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name='transferencias')
    fecha_transferencia = models.DateTimeField(default=now)
    departamento_origen = models.CharField(max_length=100)
    departamento_destino = models.CharField(max_length=100)
    transferido_por = models.CharField(max_length=100)
    recibido_por = models.CharField(max_length=100)
    cargo_entrega = models.CharField(max_length=100)
    cargo_recibe = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)
    usuario_registro = models.CharField(max_length=100)
    pdf_generado = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha_transferencia']
    
    def __str__(self):
        return f"{self.activo.codigo} - {self.departamento_origen} → {self.departamento_destino}"
