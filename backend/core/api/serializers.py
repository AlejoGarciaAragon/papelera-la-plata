from decimal import Decimal

from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.models import Caja, Categoria, Cliente, DetalleVenta, Inventario, MovimientoCaja, Producto, Venta


class PapeleraTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        grupos = list(self.user.groups.values_list('name', flat=True))
        data['role'] = 'Dueno' if 'Dueno' in grupos else grupos[0] if grupos else ''
        return data


class OcultoField(serializers.Field):
    def to_representation(self, value):
        return not value

    def to_internal_value(self, data):
        return not bool(data)


class CondicionIVAField(serializers.Field):
    labels = {
        'consumidor_final': 'Consumidor Final',
        'responsable_inscripto': 'Responsable Inscripto',
        'monotributo': 'Monotributista',
        'exento': 'Exento',
    }

    def to_representation(self, value):
        return self.labels.get(value, value)

    def to_internal_value(self, data):
        reverse = {label: key for key, label in self.labels.items()}
        value = reverse.get(data, data)
        if value not in self.labels:
            raise serializers.ValidationError('Condición frente al IVA inválida.')
        return value


class MedioPagoField(serializers.Field):
    labels = dict(Venta.METODOS_PAGO)

    def to_representation(self, value):
        return self.labels.get(value, value)

    def to_internal_value(self, data):
        reverse = {label: key for key, label in self.labels.items()}
        value = reverse.get(data, data)
        if value not in self.labels:
            raise serializers.ValidationError('Medio de pago inválido.')
        return value


class CategoriaSerializer(serializers.ModelSerializer):
    descripcion = serializers.CharField(max_length=120, allow_blank=True, allow_null=True, required=False)
    oculto = OcultoField(source='activo', required=False, default=True)

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'color', 'oculto']


class ClienteSerializer(serializers.ModelSerializer):
    razonSocial = serializers.CharField(source='nombre_o_razon_social')
    documento = serializers.CharField(source='numero_documento')
    condicionIVA = CondicionIVAField(source='condicion_iva')
    oculto = OcultoField(source='activo', required=False, default=True)

    class Meta:
        model = Cliente
        fields = ['id', 'razonSocial', 'documento', 'condicionIVA', 'direccion', 'telefono', 'email', 'oculto']
        read_only_fields = ['id']


class ProductoSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(source='codigo_barra')
    categoriaId = serializers.PrimaryKeyRelatedField(source='categoria', queryset=Categoria.objects.all(), allow_null=True, required=False)
    categoriaNombre = serializers.CharField(source='categoria.nombre', read_only=True, allow_null=True)
    precioCosto = serializers.DecimalField(source='precio_actual', max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    ganancia = serializers.DecimalField(source='porcentaje_ganancia', max_digits=7, decimal_places=2, min_value=Decimal('0'))
    precioVenta = serializers.DecimalField(source='precio_venta', max_digits=12, decimal_places=2, read_only=True)
    stock = serializers.IntegerField(write_only=True, required=False, min_value=0, default=0)
    stockMinimo = serializers.IntegerField(write_only=True, required=False, min_value=0, default=5)
    oculto = OcultoField(source='activo', required=False, default=True)

    class Meta:
        model = Producto
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'categoriaId', 'categoriaNombre', 'precioCosto', 'ganancia', 'precioVenta', 'iva', 'stock', 'stockMinimo', 'oculto']
        read_only_fields = ['id']

    def validate_categoriaId(self, value):
        if value and not value.activo and (not self.instance or self.instance.categoria_id != value.id):
            raise serializers.ValidationError('No se puede asociar un producto a una categoría oculta.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        stock = validated_data.pop('stock', 0)
        stock_minimo = validated_data.pop('stockMinimo', 5)
        producto = Producto.objects.create(**validated_data)
        Inventario.objects.create(producto=producto, stock_fisico=stock, stock_minimo=stock_minimo)
        return producto

    @transaction.atomic
    def update(self, instance, validated_data):
        stock = validated_data.pop('stock', None)
        stock_minimo = validated_data.pop('stockMinimo', None)
        instance = super().update(instance, validated_data)
        defaults = {}
        if stock is not None:
            defaults['stock_fisico'] = stock
        if stock_minimo is not None:
            defaults['stock_minimo'] = stock_minimo
        if defaults:
            Inventario.objects.update_or_create(producto=instance, defaults=defaults)
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        inventario = getattr(instance, 'inventario', None)
        data['stock'] = inventario.stock_fisico if inventario else 0
        data['stockMinimo'] = inventario.stock_minimo if inventario else 5
        return data


ProductoCreateSerializer = ProductoSerializer
ProductoUpdateSerializer = ProductoSerializer


class ProductoConsultaSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(source='codigo_barra', read_only=True)
    categoriaId = serializers.IntegerField(source='categoria_id', read_only=True, allow_null=True)
    categoriaNombre = serializers.CharField(source='categoria.nombre', read_only=True, allow_null=True)
    precioVenta = serializers.DecimalField(source='precio_venta', max_digits=12, decimal_places=2, read_only=True)
    stock = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ['id', 'codigo', 'nombre', 'categoriaId', 'categoriaNombre', 'precioVenta', 'stock', 'iva']

    def get_stock(self, obj):
        inventario = getattr(obj, 'inventario', None)
        return inventario.stock_fisico if inventario else 0


class VentaItemInputSerializer(serializers.Serializer):
    productoId = serializers.PrimaryKeyRelatedField(source='producto', queryset=Producto.objects.filter(activo=True))
    cantidad = serializers.IntegerField(min_value=1)


class VentaCreateSerializer(serializers.Serializer):
    clienteId = serializers.PrimaryKeyRelatedField(source='cliente', queryset=Cliente.objects.filter(activo=True), allow_null=True, required=False)
    tipo = serializers.ChoiceField(choices=Venta.TIPOS_COMPROBANTE)
    medioPago = MedioPagoField(source='metodo_pago', required=False)
    items = VentaItemInputSerializer(many=True, allow_empty=False)

    def validate_medioPago(self, value):
        if value == Venta.METODO_PAGO_PENDIENTE:
            raise serializers.ValidationError('Seleccioná un medio de pago válido.')
        return value


class VentaPaymentSerializer(serializers.Serializer):
    medioPago = MedioPagoField(source='metodo_pago')
    pagaCon = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0'), required=False)

    def validate(self, attrs):
        if attrs['metodo_pago'] == Venta.METODO_PAGO_PENDIENTE:
            raise serializers.ValidationError({'medioPago': 'Seleccioná un medio de pago válido.'})
        return attrs


class VentaSerializer(serializers.ModelSerializer):
    numero = serializers.SerializerMethodField()
    fecha = serializers.DateTimeField(read_only=True)
    clienteId = serializers.IntegerField(source='cliente_id', read_only=True, allow_null=True)
    clienteNombre = serializers.SerializerMethodField()
    tipo = serializers.CharField(source='tipo_comprobante', read_only=True)
    medioPago = MedioPagoField(source='metodo_pago', read_only=True)
    items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    ivaTotal = serializers.SerializerMethodField()
    cae = serializers.CharField(read_only=True)
    caeVto = serializers.DateField(source='cae_vto', read_only=True, allow_null=True)
    estadoARCA = serializers.CharField(source='estado_arca', read_only=True)
    cajaId = serializers.IntegerField(source='caja_id', read_only=True, allow_null=True)
    estado = serializers.CharField(read_only=True)
    vendedor = serializers.CharField(source='vendedor.username', read_only=True)

    class Meta:
        model = Venta
        fields = ['id', 'numero', 'fecha', 'clienteId', 'clienteNombre', 'tipo', 'medioPago', 'items', 'subtotal', 'ivaTotal', 'total', 'cae', 'caeVto', 'estadoARCA', 'cajaId', 'estado', 'vendedor']

    def get_numero(self, obj):
        return f'0001-{obj.pk:08d}'

    def get_clienteNombre(self, obj):
        return obj.cliente.nombre_o_razon_social if obj.cliente_id else 'Consumidor Final'

    def get_items(self, obj):
        return [{
            'productoId': detalle.producto_id,
            'nombre': detalle.producto.nombre,
            'cantidad': detalle.cantidad,
            'precioUnitario': detalle.precio_unitario,
            'iva': detalle.iva_porcentaje,
        } for detalle in obj.detalles.all()]

    def get_subtotal(self, obj):
        subtotal = sum((detalle.subtotal / (Decimal('1') + Decimal(detalle.iva_porcentaje) / Decimal('100')) for detalle in obj.detalles.all()), Decimal('0'))
        return subtotal.quantize(Decimal('0.01'))

    def get_ivaTotal(self, obj):
        return obj.total - self.get_subtotal(obj)


class MovimientoCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoCaja
        fields = ['id', 'fecha', 'tipo', 'concepto', 'monto']
        read_only_fields = ['id', 'fecha']


class CajaSerializer(serializers.ModelSerializer):
    fechaOperativa = serializers.DateField(source='fecha_operativa', read_only=True, allow_null=True)
    abiertaEn = serializers.DateTimeField(source='abierta_en', read_only=True)
    cerradaEn = serializers.DateTimeField(source='cerrada_en', read_only=True, allow_null=True)
    montoInicial = serializers.DecimalField(source='monto_inicial', max_digits=12, decimal_places=2, read_only=True)
    montoCierre = serializers.DecimalField(source='monto_cierre', max_digits=12, decimal_places=2, read_only=True, allow_null=True)
    usuario = serializers.CharField(source='usuario.username', read_only=True)
    movimientos = MovimientoCajaSerializer(many=True, read_only=True)

    class Meta:
        model = Caja
        fields = ['id', 'fechaOperativa', 'abiertaEn', 'cerradaEn', 'montoInicial', 'montoCierre', 'usuario', 'movimientos']


class CajaEmpleadoSerializer(serializers.ModelSerializer):
    abiertaEn = serializers.DateTimeField(source='abierta_en', read_only=True)
    usuario = serializers.CharField(source='usuario.username', read_only=True)
    montoInicial = serializers.DecimalField(source='monto_inicial', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Caja
        fields = ['id', 'abiertaEn', 'usuario', 'montoInicial']