from rest_framework import permissions

class RolAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # 1. Rechazar no autenticados
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Permisos para Dueño (acceso total)
        if request.user.groups.filter(name='Dueno').exists():
            return True

        if getattr(view, 'basename', '') == 'venta' and request.method == 'POST':
            return request.user.groups.filter(name='Empleado').exists()

        if getattr(view, 'basename', '') == 'cliente' and request.method in ['POST', 'PUT', 'PATCH']:
            return request.user.groups.filter(name='Empleado').exists()

        # 3. Permisos para Empleado (solo lectura, alta y edición de clientes)
        if request.user.groups.filter(name='Empleado').exists():
            return request.method in permissions.SAFE_METHODS

        return False