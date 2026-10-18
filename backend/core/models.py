from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.CharField(max_length=250, blank=True, null=True)
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
    tiendanube_id = models.BigIntegerField(null=True, blank=True, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo_barra} - {self.nombre}"

    @property
    def precio_venta(self):
        return self.precio_actual * (Decimal('1') + self.porcentaje_ganancia / Decimal('100'))

class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, primary_key=True, related_name='inventario')
    stock_fisico = models.IntegerField(default=0)
    stock_reservado = models.IntegerField(default=0)

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
    METODOS_PAGO = [
        (METODO_PAGO_EFECTIVO, 'Efectivo'),
        (METODO_PAGO_TARJETA, 'Tarjeta'),
        (METODO_PAGO_TRANSFERENCIA, 'Transferencia'),
    ]

    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_COMPLETADA = 'completada'
    ESTADO_CANCELADA = 'cancelada'
    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_COMPLETADA, 'Completada'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_COMPLETADA)
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

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"