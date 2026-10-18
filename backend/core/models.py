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
    cuit_dni = models.CharField(max_length=20, unique=True, db_index=True)
    razon_social = models.CharField(max_length=150)
    direccion = models.CharField(max_length=250, blank=True, null=True)
    condicion_iva = models.CharField(max_length=30)

    def __str__(self):
        return self.razon_social

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