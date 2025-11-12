from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Activo,DEPARTAMENTOS
from django.db.models import Q
from django.db.models import Count
from .forms import ActivoForm
from django import forms
from django.urls import reverse
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
from openpyxl.drawing.image import Image
import os


# 📍login 
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, 'activos/login.html')

# 📍 Lista de activos (operativos o dañados)
def lista_activos(request):
    departamento = request.GET.get("depto")
    estado = request.GET.get("estado")

    activos = Activo.objects.filter(activo=True)

    if departamento:
        activos = activos.filter(departamento=departamento)

    if estado == "dañado":
        activos = activos.filter(condicion="dañado")
    else:
        activos = activos.filter(condicion="operativo")

    context = {
        'activos': activos,
        'departamento': departamento,
        'estado': estado,
    }
    return render(request, 'activos/lista_activos.html', context)

# 📍 Registrar activo
def registrar_activo(request, departamento=None):
    if request.method == 'POST':
        form = ActivoForm(request.POST)
        if form.is_valid():
            activo = form.save(commit=False)
            activo.departamento = departamento 
            activo.condicion = 'operativo'  # 👈 Valor por defecto
            activo.activo = True
            activo.save()
            return redirect(reverse('detalle_departamento', args=[activo.departamento]))
    else:
        form = ActivoForm(initial={'departamento': departamento})

    return render(request, 'activos/registrar_activo.html', {'form': form, 'departamento': departamento})

# 📍 Editar activo
def editar_activo(request, pk):
    activo = get_object_or_404(Activo, pk=pk)
    departamento = activo.departamento

    if request.method == 'POST':
        form = ActivoForm(request.POST, instance=activo)
        if form.is_valid():
            form.save()
            return redirect(reverse('detalle_departamento', args=[departamento]))
    else:
        form = ActivoForm(instance=activo)

    return render(request, 'activos/editar_activo.html', {'form': form, 'departamento': departamento})

# 📍 Eliminar activo (eliminación lógica)
def eliminar_activo(request, pk):
    activo = get_object_or_404(Activo, pk=pk)
    departamento = activo.departamento

    if request.method == "POST":
        # 🔹 Eliminación lógica
        activo.condicion = 'dañado'      # Cambia el estado a dañado
        activo.activo = False             # Marca como inactivo
        activo.save()

        # Redirige al detalle del departamento
        return redirect(reverse('detalle_departamento', args=[departamento]))

    # Si solo se está mostrando la confirmación
    return render(request, 'activos/eliminar_activo.html', {
        'activo': activo,
        'departamento': departamento
    })

# 📍 Lista de inactivos
def lista_inactivos(request):
    q = request.GET.get("q")
    departamento = request.GET.get("depto")  # 👈 Capturamos el departamento desde la URL

    inactivos = Activo.objects.filter(activo=False)

    # Si hay departamento, filtramos
    if departamento:
        inactivos = inactivos.filter(departamento=departamento)

    # Si hay búsqueda, filtramos también
    if q:
        inactivos = inactivos.filter(
            Q(codigo__icontains=q) |
            Q(descripcion__icontains=q)
        )

    context = {
        'inactivos': inactivos,
        'departamento': departamento,  # 👈 Lo pasamos al template
    }

    return render(request, 'activos/lista_inactivos.html', context)

#📍 dash
def dashboard(request):
    # Si el usuario no está autenticado, redirige al login
    if not request.user.is_authenticated:
        return redirect('login')

    # Lista de departamentos fijos
    departamentos = [
        "Fiscalización",
        "Recaudación",
        "Inmuebles Urbanos",
        "Gerencia de Licores",
        "Gerencia General",
        "Jurídica",
        "Administración y Finanzas"
    ]

    # Si el usuario es admin → ve todo
    if request.user.is_superuser:
        activos = Activo.objects.all()
    else:
        # Usuario normal → solo su departamento
        activos = Activo.objects.filter(departamento=request.user.departamento)

    # Conteo total
    total_activos = activos.count()
    activos_operativos = activos.filter(condicion="operativo").count()
    activos_danados = activos.filter(condicion="dañado").count()
    activos_baja = activos.filter(activo=False).count()

    # Agrupar por departamento (solo para admin)
    if request.user.is_superuser:
        activos_db = activos.values('departamento').annotate(total=Count('id'))
        activos_dict = {item['departamento']: item['total'] for item in activos_db}

        activos_por_departamento = [
            {"departamento": depto, "total": activos_dict.get(depto, 0)}
            for depto in departamentos
        ]
    else:
        # Usuario normal → solo su departamento
        activos_por_departamento = [
            {"departamento": request.user.departamento, "total": total_activos}
        ]

    context = {
        "total_activos": total_activos,
        "activos_operativos": activos_operativos,
        "activos_danados": activos_danados,
        "activos_baja": activos_baja,
        "activos_por_departamento": activos_por_departamento,
        "labels": [d["departamento"] for d in activos_por_departamento],
        "data": [d["total"] for d in activos_por_departamento],
    }

    return render(request, "activos/dashboard.html", context)

#📍 restaurar
def restaurar_activo(request, id):
    activo = get_object_or_404(Activo, id=id)
    activo.activo = True
    activo.save()
    return redirect('lista_inactivos')

#📍 dash departamento
from django.shortcuts import render
from .models import Activo

def detalle_departamento(request, departamento):
    # Filtrar los activos solo del departamento seleccionado (por nombre)
    activos = Activo.objects.filter(departamento=departamento)

    # Contadores
    total_activos = activos.count()
    activos_operativos = activos.filter(condicion__icontains='Operativo').count()
    activos_danados = activos.filter(condicion__icontains='Dañado').count()
    activos_baja = activos.filter(activo=False).count()
    total_inactivos = activos.filter(activo=False).count()

    # Contexto
    context = {
        'departamento': departamento,  # ahora es texto, no objeto
        'activos': activos,
        'total_activos': total_activos,
        'activos_operativos': activos_operativos,
        'activos_danados': activos_danados,
        'activos_baja': activos_baja,
        'total_inactivos': total_inactivos,
    }

    return render(request, 'activos/detalle_departamento.html', context)


# 📍 Cerrar seccion
def logout_view(request):

    logout(request)
    return redirect('login')

# 📍 exportar todos 
def exportar_activos(request):
   # Crear el libro y hoja
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario General de Bienes"

    # -------- LOGO INSTITUCIONAL --------
    logo_path = os.path.join('activos/static/activos/img/slider5.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path)
        logo.width = 120
        logo.height = 50
        ws.add_image(logo, "A1")

    # -------- ENCABEZADO --------
    ws["B1"] = "Organismo:"
    ws["C1"] = "0001 - ALCALDÍA DE IRIBARREN"
    ws["F1"] = f"FECHA: {datetime.now().strftime('%d/%m/%Y')}"

    ws["B2"] = "Servicio:"
    ws["C2"] = "SERVICIO MUNICIPAL DE ADMINISTRACIÓN TRIBUTARIA"
    ws["B3"] = "Unidad Administrativa:"
    ws["C3"] = "SERVICIO MUNICIPAL DE ADMINISTRACIÓN TRIBUTARIA"
    ws["A4"] = "Distrito:"
    ws["B4"] = "LARA"
    ws["E4"] = "INVENTARIO GENERAL DE BIENES"
    ws["E4"].font = Font(bold=True)
    ws["A5"] = "Dirección o Lugar:"
    ws["B5"] = "CALLE 26 ENTRE CARRERAS 15 Y 16"

    ws.append([])  # espacio antes de la tabla

    # -------- ENCABEZADOS DE TABLA --------
    encabezados = ['Responsable', 'Código', 'Serial', 'Descripción', 'Estado', 'Departamento']
    ws.append(encabezados)

    header_font = Font(bold=True)
    center = Alignment(horizontal="center", vertical="center")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                         top=Side(style='thin'), bottom=Side(style='thin'))

    for cell in ws[7]:
        cell.font = header_font
        cell.alignment = center
        cell.border = thin_border

           # -------- DATOS AGRUPADOS POR RESPONSABLE --------
    activos = Activo.objects.all().order_by('responsable')

    # Agrupar por responsable
    datos = {}
    for a in activos:
        datos.setdefault(a.responsable, []).append(a)

    fila = 8  # primera fila de datos
    for responsable, bienes in datos.items():
        primera_fila = True  # bandera para saber si es la primera del grupo

        for bien in bienes:
            ws.append([
                responsable if primera_fila else '',  # solo muestra el nombre una vez
                bien.codigo,
                bien.serial,
                bien.descripcion,
                'Operativo' if bien.activo else 'Dañado',
                bien.departamento if bien.departamento else '',
            ])
            primera_fila = False  # las siguientes filas quedan vacías en responsable
            fila += 1


    # -------- BORDES Y FORMATOS --------
    for row in ws.iter_rows(min_row=8, max_row=ws.max_row, min_col=1, max_col=len(encabezados)):
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center")

    # -------- ANCHO DE COLUMNAS --------
    ancho_uniforme = 22
    for col in range(1, len(encabezados) + 1):
        ws.column_dimensions[get_column_letter(col)].width = ancho_uniforme

    # -------- RESPUESTA --------
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Inventario_General.xlsx'
    wb.save(response)
    return response

#📍 exportar por departamento 
def exportar_activos_departamento(request, departamento):
    wb = Workbook()
    ws = wb.active
    ws.title = f"Inventario {departamento}"

    # -------- LOGO INSTITUCIONAL --------
    logo_path = os.path.join('activos/static/activos/img/slider5.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path)
        logo.width = 120
        logo.height = 50
        ws.add_image(logo, "A1")

    # -------- ENCABEZADO --------
    ws["B1"] = "Organismo:"
    ws["C1"] = "0001 - ALCALDÍA DE IRIBARREN"
    ws["F1"] = f"FECHA: {datetime.now().strftime('%d/%m/%Y')}"
    ws["B2"] = "Servicio:"
    ws["C2"] = "SERVICIO MUNICIPAL DE ADMINISTRACIÓN TRIBUTARIA"
    ws["B3"] = "Unidad Administrativa:"
    ws["C3"] = "SERVICIO MUNICIPAL DE ADMINISTRACIÓN TRIBUTARIA"
    ws["A4"] = "Distrito:"
    ws["B4"] = "LARA"
    ws["E4"] = "INVENTARIO DE BIENES POR DEPARTAMENTO"
    ws["E4"].font = Font(bold=True)
    ws["A5"] = "Departamento:"
    ws["B5"] = departamento
    ws["A6"] = "Dirección o Lugar:"
    ws["B6"] = "CALLE 26 ENTRE CARRERAS 15 Y 16"

    ws.append([])

    # -------- ENCABEZADOS DE TABLA --------
    encabezados = ['Responsable', 'Código', 'Serial', 'Descripción', 'Estado']
    ws.append(encabezados)

    header_font = Font(bold=True)
    center = Alignment(horizontal="center", vertical="center")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                         top=Side(style='thin'), bottom=Side(style='thin'))

    for cell in ws[8]:
        cell.font = header_font
        cell.alignment = center
        cell.border = thin_border

    # -------- DATOS AGRUPADOS POR RESPONSABLE --------
    activos = Activo.objects.filter(departamento=departamento).order_by('responsable')
    datos = {}
    for a in activos:
        datos.setdefault(a.responsable, []).append(a)

    for responsable, bienes in datos.items():
        primera_fila = True
        for bien in bienes:
            ws.append([
                responsable if primera_fila else '',
                bien.codigo,
                bien.serial,
                bien.descripcion,
                'Operativo' if bien.activo else 'Dañado'
            ])
            primera_fila = False

    # -------- FORMATO --------
    for row in ws.iter_rows(min_row=9, max_row=ws.max_row, min_col=1, max_col=len(encabezados)):
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center")

    for col in range(1, len(encabezados) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 22

    # -------- RESPUESTA --------
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    nombre_archivo = f"Inventario_{departamento.replace(' ', '_')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={nombre_archivo}'
    wb.save(response)
    return response