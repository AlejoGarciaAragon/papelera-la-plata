from rest_framework import viewsets, status
from rest_framework.response import Response
from core.models import Categoria, Cliente, DetallePedido, Producto
from .serializers import (
    CategoriaSerializer, ClienteSerializer,
    ProductoCreateSerializer, ProductoUpdateSerializer
)
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.db.models import ProtectedError
from .permissions import RolAccessPermission

class CategoriaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RolAccessPermission]
    serializer_class = CategoriaSerializer
    queryset = Categoria.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['activo']

    def destroy(self, request, *args, **kwargs):
        categoria = self.get_object()

        if DetallePedido.objects.filter(producto__categoria=categoria).exists():
            return Response(
                {"error": "No se puede eliminar la categoría porque tiene productos asociados a ventas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        categoria.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RolAccessPermission]
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    
    # Nota: Como ModelViewSet incluye 'destroy' por defecto, si querés bloquear 
    # estrictamente el DELETE en clientes para que no se borren nunca, podés hacer esto:
    def destroy(self, request, *args, **kwargs):
        return Response(
            {"error": "Los clientes no pueden ser eliminados."},
            status=status.HTTP_403_FORBIDDEN
        )


class ProductoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RolAccessPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['categoria', 'activo']
    search_fields = ['nombre', 'codigo_barra', 'descripcion']

    def get_queryset(self):
        return Producto.objects.select_related('categoria').prefetch_related('inventario').all()

    def get_serializer_class(self):
        # Usar ProductoCreateSerializer para POST, y Update para PUT/PATCH
        if self.action in ['create', 'update', 'partial_update']:
            # Si es creación, usa el que tiene stock_inicial
            if self.action == 'create':
                return ProductoCreateSerializer
        return ProductoUpdateSerializer

    def retrieve(self, request, *args, **kwargs):
        # Impedir acceso directo por ID si el producto está inactivo
        try:
            producto = Producto.objects.get(pk=kwargs.get('pk'))
            if not producto.activo:
                return Response(
                    {"error": "El producto no está disponible."},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Producto.DoesNotExist:
            pass
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        producto = self.get_object()
        try:
            producto.delete()
        except ProtectedError:
            return Response(
                {"error": "No se puede eliminar el producto porque tiene ventas asociadas."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
