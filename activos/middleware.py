# activos/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

from activos.views import get_user_department

class DepartmentRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Solo para usuarios autenticados
        if not request.user.is_authenticated:
            return None
        
        # Si está intentando acceder al dashboard pero no es admin
        if view_func.__name__ == 'dashboard' and not request.user.is_superuser:
            user_depto = get_user_department(request.user)
            if user_depto and user_depto != "NO_ASIGNADO":
                return redirect('detalle_departamento', departamento=user_depto)
        
        return None