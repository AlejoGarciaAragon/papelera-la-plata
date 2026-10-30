from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.CharField(max_length=250, blank=True, null=True)
    color = models.CharField(max_length=7, default='#7fdcdc')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='productos')
    codigo_barra = models.CharField(max_length=50, unique=True, db_index=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio_lista = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_actual = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_ganancia = models.DecimalField(max_digits=7, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    iva = models.PositiveSmallIntegerField(default=21)
    tiendanube_id = models.BigIntegerField(null=True, blank=True, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo_barra} - {self.nombre}"

    @property
    def precio_venta(self):
        bruto = self.precio_actual * (Decimal('1') + self.porcentaje_ganancia / Decimal('100'))
        bruto *= Decimal('1') + Decimal(self.iva) / Decimal('100')
        return (bruto / Decimal('10')).quantize(Decimal('1'), rounding='ROUND_CEILING') * Decimal('10')

class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, primary_key=True, related_name='inventario')
    stock_fisico = models.IntegerField(default=0)
    stock_reservado = models.IntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"Stock: {self.stock_fisico} | {self.producto.nombre}"

class Cliente(models.Model):
    TIPO_DOCUMENTO_DNI = 'dni'
    TIPO_DOCUMENTO_CUIT = 'cuit'
    TIPO_DOCUMENTO_CUIL = 'cuil'
    TIPO_DOCUMENTO_PASAPORTE = 'pasaporte'
    TIPO_DOCUMENTO_OTRO = 'otro'
    TIPOS_DOCUMENTO = [
        (TIPO_DOCUMENTO_DNI, 'DNI'),
        (TIPO_DOCUMENTO_CUIT, 'CUIT'),
        (TIPO_DOCUMENTO_CUIL, 'CUIL'),
        (TIPO_DOCUMENTO_PASAPORTE, 'Pasaporte'),
        (TIPO_DOCUMENTO_OTRO, 'Otro'),
    ]

    CONDICION_IVA_CONSUMIDOR_FINAL = 'consumidor_final'
    CONDICION_IVA_RESPONSABLE_INSCRIPTO = 'responsable_inscripto'
    CONDICION_IVA_MONOTRIBUTO = 'monotributo'
    CONDICION_IVA_EXENTO = 'exento'
    CONDICIONES_IVA = [
        (CONDICION_IVA_CONSUMIDOR_FINAL, 'Consumidor Final'),
        (CONDICION_IVA_RESPONSABLE_INSCRIPTO, 'Responsable Inscripto'),
        (CONDICION_IVA_MONOTRIBUTO, 'Monotributo'),
        (CONDICION_IVA_EXENTO, 'Exento'),
    ]

    nombre_o_razon_social = models.CharField(max_length=200)
    tipo_documento = models.CharField(max_length=15, choices=TIPOS_DOCUMENTO, default=TIPO_DOCUMENTO_DNI)
    numero_documento = models.CharField(max_length=50, unique=True, db_index=True)
    condicion_iva = models.CharField(
        max_length=30,
        choices=CONDICIONES_IVA,
        default=CONDICION_IVA_CONSUMIDOR_FINAL,
    )
    direccion = models.CharField(max_length=250, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_o_razon_social

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True)
    precio_total = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - ${self.precio_total}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class Venta(models.Model):
    METODO_PAGO_EFECTIVO = 'efectivo'
    METODO_PAGO_TARJETA = 'tarjeta'
    METODO_PAGO_TRANSFERENCIA = 'transferencia'
    METODO_PAGO_DEBITO = 'debito'
    METODO_PAGO_CREDITO = 'credito'
    METODO_PAGO_CUENTA_DNI = 'cuenta_dni'
    METODO_PAGO_MERCADO_PAGO = 'mercado_pago'
    METODO_PAGO_PENDIENTE = 'pendiente'
    METODOS_PAGO = [
        (METODO_PAGO_EFECTIVO, 'Efectivo'),
        (METODO_PAGO_TARJETA, 'Tarjeta'),
        (METODO_PAGO_TRANSFERENCIA, 'Transferencia'),
        (METODO_PAGO_DEBITO, 'Débito'),
        (METODO_PAGO_CREDITO, 'Crédito'),
        (METODO_PAGO_CUENTA_DNI, 'Cuenta DNI'),
        (METODO_PAGO_MERCADO_PAGO, 'Mercado Pago'),
        (METODO_PAGO_PENDIENTE, 'Pendiente de cobro'),
    ]

    TIPO_FACTURA_A = 'Factura A'
    TIPO_FACTURA_B = 'Factura B'
    TIPO_FACTURA_C = 'Factura C'
    TIPO_FACTURA_X = 'Factura X'
    TIPOS_COMPROBANTE = [
        (TIPO_FACTURA_A, 'Factura A'),
        (TIPO_FACTURA_B, 'Factura B'),
        (TIPO_FACTURA_C, 'Factura C'),
        (TIPO_FACTURA_X, 'Factura X'),
    ]

    ESTADO_PENDIENTE_COBRO = 'pendiente_cobro'
    ESTADO_PENDIENTE = ESTADO_PENDIENTE_COBRO
    ESTADO_COMPLETADA = 'completada'
    ESTADO_CANCELADA = 'cancelada'
    ESTADOS = [
        (ESTADO_PENDIENTE_COBRO, 'Pendiente de cobro'),
        (ESTADO_COMPLETADA, 'Completada'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    tipo_comprobante = models.CharField(max_length=20, choices=TIPOS_COMPROBANTE, default=TIPO_FACTURA_B)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_COMPLETADA)
    nro_comprobante = models.CharField(max_length=20, blank=True, default='')
    cae = models.CharField(max_length=20, blank=True, default='')
    vencimiento_cae = models.DateField(null=True, blank=True)
    estado_arca = models.CharField(max_length=20, default='Pendiente')
    caja = models.ForeignKey('Caja', on_delete=models.PROTECT, null=True, blank=True, related_name='ventas')
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='ventas',
    )
    vendedor = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='ventas')

    def __str__(self):
        return f"Venta #{self.id} - ${self.total}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_venta')
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    iva_porcentaje = models.PositiveSmallIntegerField(default=21)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class Caja(models.Model):
    usuario = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='cajas')
    fecha_operativa = models.DateField(null=True, blank=True, unique=True, editable=False)
    abierta_en = models.DateTimeField(auto_now_add=True)
    cerrada_en = models.DateTimeField(null=True, blank=True)
    monto_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_cierre = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Caja #{self.pk}"


class MovimientoCaja(models.Model):
    TIPO_INGRESO = 'Ingreso'
    TIPO_EGRESO = 'Egreso'
    TIPOS = [(TIPO_INGRESO, 'Ingreso'), (TIPO_EGRESO, 'Egreso')]

    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='movimientos')
    usuario = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='movimientos_caja')
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    concepto = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.tipo}: {self.concepto}"