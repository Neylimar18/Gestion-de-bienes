
from django.shortcuts import redirect
from django.urls import path
from django.contrib.auth.decorators import login_required  # <-- AÑADE ESTE IMPORT
from . import views


urlpatterns = [

    # Redirección inicial (ajusta según prefieras)
    path('', lambda request: redirect('login')),

    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard principal
    path('dash/', views.dashboard, name='dashboard'),

    # Activos por departamento
    path('departamento/<str:departamento>/', views.detalle_departamento, name='detalle_departamento'),
    path('departamento/<str:departamento>/crear/', views.registrar_activo, name='crear_activo_departamento'),
    path('activos/departamento/<str:departamento>/', views.activos_departamento, name='activos_departamento'),


    # Listas de activos
    path('editar/<int:id>/', views.editar_activo, name='editar_activo'),
    path('eliminar/<int:pk>/', views.eliminar_activo, name='eliminar_activo'),
    path('exportar-activos/', views.exportar_activos, name='exportar_activos'),
    path('exportar-activos/<str:departamento>/', views.exportar_activos_departamento, name='exportar_activos_departamento'),
    path('cambiar-clave/', views.simple_password_change, name='simple_password_change'),
    path('activos/', views.lista_activos, name='lista_activos'),
    path('exportar-pdf-activos/', views.exportar_pdf_activos, name='exportar_pdf_activos'),
    path('exportar-pdf-departamento/<str:departamento>/', views.exportar_pdf_activos_departamento, name='exportar_pdf_departamento'),

    # Cambio de contraseña (logueado)
    path('cambiar-password/', login_required(views.simple_password_change), name='simple_password_change'),
    
    # Recuperación de contraseña (olvidé)
    path('olvide-password/', views.password_reset_request, name='password_reset_request'),
    
    path('reset-password-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
]
    