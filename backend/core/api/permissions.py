from rest_framework import permissions

class RolAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.groups.filter(name='Dueno').exists():
            return True

        if not request.user.groups.filter(name='Empleado').exists():
            return False

        basename = getattr(view, 'basename', '')
        action = getattr(view, 'action', '')
        if basename == 'categoria':
            return request.method in permissions.SAFE_METHODS
        if basename == 'producto':
            return request.method in permissions.SAFE_METHODS
        if basename == 'caja':
            if request.method == 'GET':
                return action == 'actual'
            return request.method == 'POST' and action == 'abrir'
        if basename == 'venta':
            return request.method == 'POST' and action == 'create'

        return False