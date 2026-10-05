from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='productos')
    codigo_barra = models.CharField(max_length=50, unique=True, db_index=True)
    nombre = models.CharField(max_length=150)
    precio_actual = models.DecimalField(max_digits=10, decimal_places=2)
    tiendanube_id = models.BigIntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.codigo_barra} - {self.nombre}"

class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, primary_key=True, related_name='inventario')
    stock_fisico = models.IntegerField(default=0)
    stock_reservado = models.IntegerField(default=0)

    def __str__(self):
        return f"Stock: {self.stock_fisico} | {self.producto.nombre}"

class Cliente(models.Model):
    cuit_dni = models.CharField(max_length=20, unique=True, db_index=True)
    razon_social = models.CharField(max_length=150)
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