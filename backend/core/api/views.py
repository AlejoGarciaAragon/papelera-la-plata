from decimal import Decimal

from datetime import date

from rest_framework import viewsets, status
from rest_framework.decorators import action
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
from django.db.models import Sum
from django.utils import timezone
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
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['nombre_o_razon_social', 'numero_documento']
    filterset_fields = ['condicion_iva', 'activo']

    def destroy(self, request, *args, **kwargs):
        cliente = self.get_object()
        try:
            cliente.delete()
        except ProtectedError:
            return Response(
                {
                    "error": (
                        "No se puede eliminar el cliente porque tiene ventas, pedidos "
                        "u otras operaciones asociadas."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    queryset = Venta.objects.select_related('vendedor', 'cliente').prefetch_related('detalles__producto').all()
    serializer_class = VentaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['estado', 'metodo_pago', 'vendedor']
    search_fields = ['vendedor__username', 'detalles__producto__nombre', 'detalles__producto__codigo_barra']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        fecha = params.get('fecha')
        fecha_desde = params.get('fecha_desde')
        fecha_hasta = params.get('fecha_hasta')

        if fecha:
            queryset = queryset.filter(fecha__date=fecha)
        if fecha_desde:
            queryset = queryset.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__date__lte=fecha_hasta)
        return queryset.distinct()

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
                cliente=serializer.validated_data.get('cliente'),
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

    @action(detail=False, methods=['get'])
    def resumen_diario(self, request):
        fecha = request.query_params.get('fecha')
        if not fecha:
            fecha = timezone.localdate().isoformat()
        try:
            date.fromisoformat(fecha)
        except ValueError:
            raise ValidationError({'fecha': 'Usá el formato YYYY-MM-DD.'})

        ventas = Venta.objects.filter(fecha__date=fecha, estado=Venta.ESTADO_COMPLETADA)
        recaudacion_por_metodo = {
            metodo: ventas.filter(metodo_pago=metodo).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
            for metodo, _ in Venta.METODOS_PAGO
        }
        return Response({
            'fecha': fecha,
            'cantidad_ventas': ventas.count(),
            'recaudacion_total': ventas.aggregate(total=Sum('total'))['total'] or Decimal('0.00'),
            'recaudacion_por_metodo': recaudacion_por_metodo,
        })

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        if not request.user.groups.filter(name='Dueno').exists():
            return Response(
                {'error': 'Solo el rol Dueño puede anular ventas.'},
                status=status.HTTP_403_FORBIDDEN
            )

        with transaction.atomic():
            venta = Venta.objects.select_for_update().prefetch_related('detalles').get(pk=pk)
            if venta.estado != Venta.ESTADO_COMPLETADA:
                return Response(
                    {'error': 'Solo se pueden anular ventas completadas.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            detalles = list(venta.detalles.all())
            inventarios = {
                inventario.producto_id: inventario
                for inventario in Inventario.objects.select_for_update().filter(
                    producto_id__in=[detalle.producto_id for detalle in detalles]
                )
            }
            for detalle in detalles:
                inventario = inventarios.get(detalle.producto_id)
                if inventario is None:
                    raise ValidationError({'stock': f'No existe inventario para "{detalle.producto}".'})
                inventario.stock_fisico += detalle.cantidad
                inventario.save(update_fields=['stock_fisico'])

            venta.estado = Venta.ESTADO_CANCELADA
            venta.save(update_fields=['estado'])

        return Response(self.get_serializer(venta).data)
