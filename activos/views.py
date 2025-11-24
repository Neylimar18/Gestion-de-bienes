import os
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
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render
from .models import Activo
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from django.conf import settings



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

# 📍 Registrar activo
def registrar_activo(request, departamento=None):
    if request.method == 'POST':
        form = ActivoForm(request.POST)
        if form.is_valid():
            activo = form.save(departamento=departamento)
            return redirect('detalle_departamento', departamento=activo.departamento)
    else:
        form = ActivoForm()

    return render(request, 'activos/registrar_activo.html', {
        'form': form, 
        'departamento': departamento
    })

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

#📍 dash
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Lista de departamentos fijos - CORREGIDA (faltaba coma)
    departamentos = [
        "Fiscalización",
        "Recaudación", 
        "Inmuebles Urbanos",
        "Gerencia de Licores",
        "Gerencia General",
        "Jurídica",
        "Informatica",  # CORREGIDO: agregada coma
        "Administración y Finanzas"
    ]

    # Si el usuario es admin → ve todo
    if request.user.is_superuser:
        activos = Activo.objects.all()
    else:
        # Usuario normal → solo su departamento
        activos = Activo.objects.filter(departamento=request.user.departamento)

    # Conteo total - CORREGIDO: usar minúsculas
    total_activos = activos.count()
    activos_operativos = activos.filter(condicion="operativo").count()  # minúscula
    activos_danados = activos.filter(condicion="dañado").count()        # minúscula
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

#📍 dash departamento
def detalle_departamento(request, departamento):
    # Filtrar los activos solo del departamento seleccionado (por nombre)
    activos = Activo.objects.filter(departamento=departamento)

    # Contadores
    total_activos = activos.count()
    activos_operativos = activos.filter(condicion__icontains='Operativo').count()
    activos_danados = activos.filter(condicion__icontains='Dañado').count()
    

    # Contexto
    context = {
        'departamento': departamento,  # ahora es texto, no objeto
        'activos': activos,
        'total_activos': total_activos,
        'activos_operativos': activos_operativos,
        'activos_danados': activos_danados,
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
                bien.get_condicion_display(),
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
                bien.get_condicion_display()
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


def simple_password_change(request):
    """
    Vista simplificada para cambiar contraseña directamente
    """
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validar que las contraseñas coincidan
        if new_password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'activos/simple_password_change.html')
        
        # Validar longitud mínima
        if len(new_password) < 4:  # Puedes ajustar este requisito
            messages.error(request, 'La contraseña debe tener al menos 4 caracteres')
            return render(request, 'activos/simple_password_change.html')
        
        # Aquí normalmente buscarías al usuario por email, username, etc.
        # Por ahora usamos un usuario de ejemplo
        try:
            # En un caso real, aquí identificarías al usuario
            # user = User.objects.get(email=email) o por otro campo
            user = request.user if request.user.is_authenticated else User.objects.first()
            
            if user:
                user.set_password(new_password)
                user.save()
                
                # Si el usuario estaba autenticado, mantener la sesión
                if request.user.is_authenticated:
                    from django.contrib.auth import update_session_auth_hash
                    update_session_auth_hash(request, user)
                
                messages.success(request, 'Contraseña cambiada exitosamente')
                return redirect('login')
            else:
                messages.error(request, 'No se pudo encontrar el usuario')
                
        except Exception as e:
            messages.error(request, f'Error al cambiar la contraseña: {str(e)}')
    
    return render(request, 'activos/simple_password_change.html')

# 📍 Lista de activos (operativos o dañados)
def lista_activos(request):
    departamento = request.GET.get("depto")
    estado = request.GET.get("estado")

    # Iniciar con todos los activos (activos=True)
    activos = Activo.objects.filter(activo=True)

    if departamento:
        activos = activos.filter(departamento=departamento)

    # CORRECCIÓN: Usar los valores exactos del modelo en minúsculas
    if estado:
        if estado == "dañado":
            activos = activos.filter(condicion="dañado")  # minúscula
        elif estado == "operativo":
            activos = activos.filter(condicion="operativo")  # minúscula

    context = {
        'activos': activos,
        'departamento': departamento,
        'estado': estado,
    }
    return render(request, 'activos/lista_activos.html', context)


# 📍 Eliminar activo (eliminación lógica)
def eliminar_activo(request, pk):
    activo = get_object_or_404(Activo, pk=pk)
    departamento = activo.departamento

    if request.method == "POST":
        # 🔹 Eliminación lógica - CORRECCIÓN: usar minúsculas
        activo.condicion = 'dañado'      # CORREGIDO: minúscula
        activo.activo = True       
        activo.save()

        messages.success(request, f'Activo {activo.codigo} marcado como dañado')
        return redirect(reverse('detalle_departamento', args=[departamento]))

    return render(request, 'activos/eliminar_activo.html', {
        'activo': activo,
        'departamento': departamento
    })

#📍 Lista de activos (operativos o dañados) DEPARTAMENTOS
def activos_departamento(request, departamento):
    activos = Activo.objects.filter(departamento=departamento, activo=True)

    estado = request.GET.get('estado')
    buscar = request.GET.get('buscar')

    if buscar:
        activos = activos.filter(
        Q(serial__icontains=buscar) |
        Q(descripcion__icontains=buscar)
    )   
    # Filtro por estado
    if estado:
        if estado == "dañado":
            activos = activos.filter(condicion="dañado")  # minúscula
        elif estado == "operativo":
            activos = activos.filter(condicion="operativo")  # minúscula


    context = {
        "activos": activos,
        "departamento": departamento,
        "estado": estado
    }

    return render(request, "activos/activos_departamento.html", context)

from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.http import HttpResponse
import os
from datetime import datetime
from .models import Activo

def exportar_pdf_activos(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Inventario_General.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, 
                            topMargin=40, bottomMargin=40, 
                            leftMargin=40, rightMargin=40)
    elements = []
    estilos = getSampleStyleSheet()
    
    estilo_centrado = ParagraphStyle(
        name='Centrado',
        parent=estilos['Normal'],
        alignment=TA_CENTER,
        fontSize=10,
        fontName='Times-Roman'
    )

    # Cargar logos
    logo1_path = os.path.join(settings.BASE_DIR, "activos/static/activos/img/logo1.jpg")
    logo2_path = os.path.join(settings.BASE_DIR, "activos/static/activos/img/slider1.jpg")

    logo1 = Image(logo1_path, width=70, height=70) if os.path.exists(logo1_path) else Paragraph("LOGO 1", estilo_centrado)
    logo2 = Image(logo2_path, width=70, height=70) if os.path.exists(logo2_path) else Paragraph("LOGO 2", estilo_centrado)

    texto_encabezado = Paragraph("""
        <b>República Bolivariana de Venezuela</b><br/>
        <b>Estado Lara</b><br/>
        <b>Alcaldía Bolivariana del Municipio Iribarren</b><br/>
        <b>Servicio Municipal de Administración Tributaria</b><br/>
        <b>SEMAT</b>
    """, estilo_centrado)

    encabezado = Table([[logo1, texto_encabezado, logo2]], colWidths=[80, 400, 80])
    encabezado.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
    ]))
    elements.append(encabezado)
    elements.append(Spacer(1, 20))

    # Estilos personalizados
    estilos.add(ParagraphStyle(name='TituloPrincipal', parent=estilos['Heading1'],
                               fontSize=16, textColor=colors.black, alignment=TA_CENTER,
                               spaceAfter=20, spaceBefore=10, fontName='Times-Bold'))

    estilos.add(ParagraphStyle(name='CeldaNormal', parent=estilos['Normal'],
                               fontSize=8, textColor=colors.black, alignment=TA_CENTER,
                               fontName='Times-Roman'))

    estilos.add(ParagraphStyle(name='CeldaEncabezado', parent=estilos['Normal'],
                               fontSize=9, textColor=colors.black, alignment=TA_CENTER,
                               fontName='Times-Bold'))

    # Título principal
    elements.append(Paragraph("INVENTARIO GENERAL DE BIENES", estilos['TituloPrincipal']))
    elements.append(Spacer(1, 15))

    # Tabla de datos
    encabezados = ['Nº', 'Responsable', 'Codigo', 'Serial','Descripción','Categoria','Subcategoria', 'Estado', 'Departamento']
    data = [encabezados]

    activos = Activo.objects.all().order_by("codigo")

    for idx, activo in enumerate(activos, 1):
        # Estado
        if activo.condicion == "operativo":
            estado_text = "Operativo"
        elif activo.condicion == "dañado":
            estado_text = "Dañado"
        else:
            estado_text = activo.get_condicion_display()

        # Categoría y subcategoría
        categoria_text = activo.categoria_principal.replace('_', ' ').title() if activo.categoria_principal else ""
        subcategoria_text = activo.subcategoria.replace('_', ' ').title() if activo.subcategoria else ""

        fila = [
            Paragraph(str(idx), estilos['CeldaNormal']),
            Paragraph(activo.responsable or "", estilos['CeldaNormal']),
            Paragraph(activo.codigo or "", estilos['CeldaNormal']),
            Paragraph(activo.serial or "", estilos['CeldaNormal']),
            Paragraph(activo.descripcion or "", estilos['CeldaNormal']),
            Paragraph(categoria_text, estilos['CeldaNormal']),
            Paragraph(subcategoria_text, estilos['CeldaNormal']),
            Paragraph(estado_text, estilos['CeldaNormal']),
            Paragraph(activo.departamento or "", estilos['CeldaNormal']),
        ]
        data.append(fila)

    # Si no hay activos, agregar filas vacías
    if not activos:
        for _ in range(3):
            fila_vacia = [Paragraph("", estilos['CeldaNormal']) for _ in range(9)]
            data.append(fila_vacia)

    tabla = Table(data, repeatRows=1, colWidths=[20, 60, 50, 60, 60, 70, 70, 40, 60])
    tabla.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))
    elements.append(tabla)
    elements.append(Spacer(1, 20))

    # Pie de página
    def pie_pagina(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.black)
        canvas.drawString(40, 25, "SEMAT - Sistema de Gestión de Activos")
        canvas.drawRightString(doc.pagesize[0] - 40, 30, str(doc.page))
        canvas.restoreState()

    doc.build(elements, onFirstPage=pie_pagina, onLaterPages=pie_pagina)

    return response