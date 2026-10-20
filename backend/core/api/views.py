from decimal import Decimal

from datetime import date

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Caja, Categoria, Cliente, DetallePedido, DetalleVenta, Inventario, MovimientoCaja, Producto, Venta
from .serializers import (
    CajaEmpleadoSerializer, CajaSerializer, CategoriaSerializer, ClienteSerializer, MovimientoCajaSerializer,
    ProductoConsultaSerializer, ProductoCreateSerializer, ProductoUpdateSerializer,
    VentaCreateSerializer, VentaPaymentSerializer, VentaSerializer
)
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.db.models import ProtectedError
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .permissions import RolAccessPermission


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        grupos = list(request.user.groups.values_list('name', flat=True))
        return Response({
            'usuario': request.user.username,
            'nombre': request.user.get_full_name() or request.user.username,
            'rol': 'Dueno' if 'Dueno' in grupos else grupos[0] if grupos else '',
        })

class CategoriaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RolAccessPermission]
    serializer_class = CategoriaSerializer
    queryset = Categoria.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['activo']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.groups.filter(name='Empleado').exists() and not self.request.user.groups.filter(name='Dueno').exists():
            queryset = queryset.filter(activo=True)
        return queryset

    def destroy(self, request, *args, **kwargs):
        categoria = self.get_object()

        if categoria.productos.exists() or DetallePedido.objects.filter(producto__categoria=categoria).exists():
            return Response(
            {"error": "No se puede eliminar la categoría porque tiene productos u operaciones asociados."},
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
        queryset = Producto.objects.select_related('categoria').prefetch_related('inventario')
        if self.request.user.groups.filter(name='Empleado').exists() and not self.request.user.groups.filter(name='Dueno').exists():
            queryset = queryset.filter(activo=True)
        return queryset

    def get_serializer_class(self):
        if self.request.user.groups.filter(name='Empleado').exists() and not self.request.user.groups.filter(name='Dueno').exists():
            return ProductoConsultaSerializer
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


class CajaViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, RolAccessPermission]
    serializer_class = CajaSerializer
    queryset = Caja.objects.select_related('usuario').prefetch_related('movimientos', 'ventas__detalles__producto').all()

    def get_serializer_class(self):
        if self.request.user.groups.filter(name='Empleado').exists() and not self.request.user.groups.filter(name='Dueno').exists():
            return CajaEmpleadoSerializer
        return CajaSerializer

    @action(detail=False, methods=['get'])
    def actual(self, request):
        caja = Caja.objects.filter(cerrada_en__isnull=True).first()
        if caja is None:
            return Response(None)
        return Response(self.get_serializer(caja).data)

    @action(detail=False, methods=['get'])
    def ultima_cerrada(self, request):
        caja = Caja.objects.filter(cerrada_en__isnull=False).order_by('-cerrada_en').first()
        if caja is None:
            return Response(None)
        return Response(self.get_serializer(caja).data)

    @action(detail=False, methods=['post'])
    def abrir(self, request):
        monto = request.data.get('montoInicial', 0)
        try:
            monto = Decimal(str(monto))
            if monto < 0:
                raise ValueError
        except Exception:
            raise ValidationError({'montoInicial': 'Ingresá un monto válido mayor o igual a cero.'})
        fecha_operativa = timezone.localdate()
        try:
            with transaction.atomic():
                if Caja.objects.filter(fecha_operativa=fecha_operativa).exists():
                    raise ValidationError({'caja': 'Ya se abrió una caja para este día.'})
                if Caja.objects.select_for_update().filter(cerrada_en__isnull=True).exists():
                    raise ValidationError({'caja': 'Cerrá la caja abierta antes de iniciar otra.'})
                caja = Caja.objects.create(
                    usuario=request.user,
                    monto_inicial=monto,
                    fecha_operativa=fecha_operativa,
                )
        except IntegrityError:
            raise ValidationError({'caja': 'Ya se abrió una caja para este día.'})
        return Response(self.get_serializer(caja).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        try:
            monto = Decimal(str(request.data.get('montoCierre')))
            if monto < 0:
                raise ValueError
        except Exception:
            raise ValidationError({'montoCierre': 'Ingresá un monto válido mayor o igual a cero.'})
        with transaction.atomic():
            caja = Caja.objects.select_for_update().get(pk=pk)
            if caja.cerrada_en:
                raise ValidationError({'caja': 'La caja ya está cerrada.'})
            if caja.ventas.filter(estado=Venta.ESTADO_PENDIENTE).exists():
                raise ValidationError({'caja': 'No se puede cerrar la caja mientras haya ventas pendientes de cobro.'})
            caja.cerrada_en = timezone.now()
            caja.monto_cierre = monto
            caja.save(update_fields=['cerrada_en', 'monto_cierre'])
        return Response(self.get_serializer(caja).data)

    @action(detail=True, methods=['post'])
    def movimientos(self, request, pk=None):
        caja = self.get_object()
        if caja.cerrada_en:
            raise ValidationError({'caja': 'No se pueden registrar movimientos en una caja cerrada.'})
        serializer = MovimientoCajaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        movimiento = MovimientoCaja.objects.create(caja=caja, usuario=request.user, **serializer.validated_data)
        return Response(MovimientoCajaSerializer(movimiento).data, status=status.HTTP_201_CREATED)


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
        serializer = VentaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        es_dueno = request.user.groups.filter(name='Dueno').exists()
        if es_dueno and 'metodo_pago' not in values:
            raise ValidationError({'medioPago': 'Seleccioná el medio de pago.'})
        if es_dueno and values.get('metodo_pago') == Venta.METODO_PAGO_PENDIENTE:
            raise ValidationError({'medioPago': 'Seleccioná un medio de pago válido.'})
        metodo_pago = values.get('metodo_pago') if es_dueno else Venta.METODO_PAGO_PENDIENTE
        items = values['items']

        productos_ids = [item['producto'].id for item in items]
        if len(productos_ids) != len(set(productos_ids)):
            raise ValidationError({'items': 'No se puede repetir un producto en la misma venta.'})

        with transaction.atomic():
            caja = Caja.objects.select_for_update().filter(cerrada_en__isnull=True).first()
            if caja is None:
                raise ValidationError({'caja': 'Abrí una caja antes de registrar una venta.'})
            inventarios = {}
            for item in items:
                try:
                    inventario = Inventario.objects.select_for_update().select_related('producto').get(
                        producto_id=item['producto'].id
                    )
                except Inventario.DoesNotExist:
                    raise ValidationError({'items': f"El producto {item['producto'].id} no tiene inventario."})

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

            total = Decimal('0.00')
            for _, producto, cantidad in inventarios.values():
                total += producto.precio_venta * cantidad
            venta = Venta.objects.create(
                total=total,
                metodo_pago=metodo_pago,
                tipo_comprobante=values['tipo'],
                cliente=values.get('cliente') if es_dueno else None,
                estado=Venta.ESTADO_COMPLETADA if es_dueno else Venta.ESTADO_PENDIENTE,
                estado_arca='No aplica' if values['tipo'] == Venta.TIPO_FACTURA_X else 'Pendiente',
                vendedor=request.user,
                caja=caja,
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
                    subtotal=subtotal,
                    iva_porcentaje=producto.iva,
                )

        return Response(self.get_serializer(venta).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cobrar(self, request, pk=None):
        serializer = VentaPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            venta = Venta.objects.select_for_update().get(pk=pk)
            if venta.estado != Venta.ESTADO_PENDIENTE:
                raise ValidationError({'venta': 'La venta ya no está pendiente de cobro.'})
            if not venta.caja_id:
                raise ValidationError({'caja': 'Se necesita una caja abierta para cobrar esta venta.'})
            caja = Caja.objects.select_for_update().get(pk=venta.caja_id)
            if caja.cerrada_en:
                raise ValidationError({'caja': 'Se necesita una caja abierta para cobrar esta venta.'})
            metodo_pago = serializer.validated_data['metodo_pago']
            paga_con = serializer.validated_data.get('pagaCon')
            if metodo_pago == Venta.METODO_PAGO_EFECTIVO and (paga_con is None or paga_con < venta.total):
                raise ValidationError({'pagaCon': 'Ingresá un importe igual o mayor al total de la venta.'})
            venta.metodo_pago = metodo_pago
            venta.estado = Venta.ESTADO_COMPLETADA
            update_fields = ['metodo_pago', 'estado']
            if 'cliente' in serializer.validated_data:
                venta.cliente = serializer.validated_data['cliente']
                update_fields.append('cliente')
            venta.save(update_fields=update_fields)
        return Response(self.get_serializer(venta).data)

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
            label: ventas.filter(metodo_pago=metodo).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
            for metodo, label in Venta.METODOS_PAGO
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
