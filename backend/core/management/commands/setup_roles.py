from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from core.models import Categoria, Producto, Cliente

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea roles RBAC, asigna permisos nativos y genera usuarios de prueba.'

    def handle(self, *args, **options):
        # 1. Crear grupos
        grupo_dueno, _ = Group.objects.get_or_create(name='Dueno')
        grupo_empleado, _ = Group.objects.get_or_create(name='Empleado')

        # 2. Limpiar y reasignar permisos al Dueño
        grupo_dueno.permissions.clear()
        modelos = [Categoria, Producto, Cliente]
        for modelo in modelos:
            ct = ContentType.objects.get_for_model(modelo)
            permisos = Permission.objects.filter(content_type=ct)
            grupo_dueno.permissions.add(*permisos)

        # 3. Limpiar y reasignar permisos al Empleado (Solo View según matriz)
        grupo_empleado.permissions.clear()
        for modelo in modelos:
            ct = ContentType.objects.get_for_model(modelo)
            permiso_view = Permission.objects.filter(content_type=ct, codename__startswith='view_')
            grupo_empleado.permissions.add(*permiso_view)

        # 4. Configurar usuarios
        usuarios = [
            {'username': 'dueno_test', 'email': 'dueno@test.com', 'grupo': grupo_dueno},
            {'username': 'empleado_test', 'email': 'empleado@test.com', 'grupo': grupo_empleado}
        ]

        for u in usuarios:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={'email': u['email'], 'is_superuser': False, 'is_staff': False}
            )
            if created:
                user.set_password('password123')
            user.groups.clear()
            user.groups.add(u['grupo'])
            user.save()

        self.stdout.write(self.style.SUCCESS('Roles y usuarios configurados exitosamente.'))