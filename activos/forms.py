from django import forms
from .models import Activo, CATEGORIAS_PRINCIPALES, SUBCATEGORIAS

class ActivoForm(forms.ModelForm):
    
    class Meta:
        model = Activo
        fields = ['categoria_principal', 'subcategoria', 'codigo', 'serial', 'descripcion', 'responsable']
        widgets = {
            'categoria_principal': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'categoria_principal'
            }),
            'subcategoria': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'subcategoria'
            }),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'serial': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del responsable'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar con todas las subcategorías disponibles
        self.fields['subcategoria'].choices = [('', 'Seleccione una categoría principal primero')] + list(SUBCATEGORIAS)

    def clean(self):
        cleaned_data = super().clean()
        categoria_principal = cleaned_data.get('categoria_principal')
        subcategoria = cleaned_data.get('subcategoria')
        
        # Solo validar si ambos campos están completos
        if categoria_principal and subcategoria:
            # Definir qué subcategorías pertenecen a cada categoría principal
            categorias_validas = {
                'equipo_informatico': ['pc_escritorio', 'laptop', 'tablet', 'servidor', 'impresora', 'monitor', 'teclado', 'mouse'],
                'mueble': ['escritorio', 'silla', 'archivador', 'estanteria', 'mesa'],
                'equipo_especializado': ['scanner', 'proyector', 'telefono', 'switch', 'router'],
                'otro': ['otro_equipo', 'herramienta', 'material']
            }
            
            if categoria_principal in categorias_validas:
                subcategorias_permitidas = categorias_validas[categoria_principal]
                if subcategoria not in subcategorias_permitidas:
                    self.add_error('subcategoria', f'"{subcategoria}" no es válido para la categoría "{categoria_principal}".')
        
        return cleaned_data

    def save(self, commit=True, departamento=None):
        activo = super().save(commit=False)
        activo.condicion = 'operativo'
        activo.activo = True
        if departamento:
            activo.departamento = departamento
        
        if commit:
            activo.save()
        return activo