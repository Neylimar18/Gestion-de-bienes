from django import forms
from .models import Activo

class ActivoForm(forms.ModelForm):
    class Meta:
        model = Activo
        # 🔹 Quitamos 'condicion' y 'activo' del formulario
        fields = ['codigo', 'serial', 'descripcion', 'responsable']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'serial': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True, departamento=None):
        activo = super().save(commit=False)
        # 🔹 Estos valores se asignan automáticamente
        activo.condicion = 'operativo'
        activo.activo = True
        if departamento:
            activo.departamento = departamento  # ✅ Se asigna dinámicamente desde la vista
        if commit:
            activo.save()
        return activo
