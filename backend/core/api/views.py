from decimal import Decimal

from rest_framework import viewsets, status
from rest_framework.response import Response
from core.models import Categoria, Cliente, DetallePedido, DetalleVenta, Inventario, Producto, Venta
from .serializers import (
    CategoriaSerializer, ClienteSerializer,
    ProductoCreateSerializer, ProductoUpdateSerializer, VentaSerializer
)
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.db.models import ProtectedError
from django.db import transaction
from rest_framework.exceptions import ValidationError
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


class VentaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RolAccessPermission]
    queryset = Venta.objects.select_related('vendedor').prefetch_related('detalles__producto').all()
    serializer_class = VentaSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items = serializer.validated_data.pop('items')

        productos_ids = [item['producto_id'] for item in items]
        if len(productos_ids) != len(set(productos_ids)):
            raise ValidationError({'items': 'No se puede repetir un producto en la misma venta.'})

        with transaction.atomic():
            inventarios = {}
            for item in items:
                try:
                    inventario = Inventario.objects.select_for_update().select_related('producto').get(
                        producto_id=item['producto_id']
                    )
                except Inventario.DoesNotExist:
                    raise ValidationError({'items': f"El producto {item['producto_id']} no tiene inventario."})

                producto = inventario.producto
                if not producto.activo:
                    raise ValidationError({'items': f'El producto "{producto.nombre}" está inactivo.'})
                cantidad = item['cantidad']
                stock_disponible = inventario.stock_fisico - inventario.stock_reservado
                if stock_disponible < cantidad:
                    raise ValidationError({
                        'stock': f'No hay stock suficiente para "{producto.nombre}". Disponible: {stock_disponible}.'
                    })
                inventarios[producto.id] = (inventario, producto, cantidad)

            total = sum(
                (producto.precio_venta * cantidad for _, producto, cantidad in inventarios.values()),
                Decimal('0.00')
            )
            venta = Venta.objects.create(
                total=total,
                metodo_pago=serializer.validated_data['metodo_pago'],
                estado=Venta.ESTADO_COMPLETADA,
                vendedor=request.user
            )
            for inventario, producto, cantidad in inventarios.values():
                precio_unitario = producto.precio_venta
                subtotal = precio_unitario * cantidad
                inventario.stock_fisico -= cantidad
                inventario.save(update_fields=['stock_fisico'])
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal
                )

        return Response(self.get_serializer(venta).data, status=status.HTTP_201_CREATED)
