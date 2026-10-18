from rest_framework import permissions

class RolAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # 1. Rechazar no autenticados
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Bloqueo global: Nadie puede eliminar clientes
        if request.method == 'DELETE' and getattr(view, 'basename', '') == 'cliente':
            return False

        # 3. Permisos para Dueño (Acceso total al resto)
        if request.user.groups.filter(name='Dueno').exists():
            return True

        if getattr(view, 'basename', '') == 'venta' and request.method == 'POST':
            return request.user.groups.filter(name='Empleado').exists()

        # 4. Permisos para Empleado (Solo lectura: GET, HEAD, OPTIONS)
        if request.user.groups.filter(name='Empleado').exists():
            return request.method in permissions.SAFE_METHODS

        return False