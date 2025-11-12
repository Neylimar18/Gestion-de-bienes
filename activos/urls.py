
from django.shortcuts import redirect
from django.urls import path
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

    # Listas de activos
    path('activos/', views.lista_activos, name='lista_activos'),
    path('inactivos/', views.lista_inactivos, name='lista_inactivos'),
    path('editar/<int:id>/', views.editar_activo, name='editar_activo'),
    path('eliminar/<int:pk>/', views.eliminar_activo, name='eliminar_activo'),
    path('restaurar/<int:id>/', views.restaurar_activo, name='restaurar_activo'),
    path('exportar-activos/', views.exportar_activos, name='exportar_activos'),
   path('departamento/<str:departamento>/exportar_excel/', views.exportar_activos_departamento, name='exportar_activos_departamento'),

]
