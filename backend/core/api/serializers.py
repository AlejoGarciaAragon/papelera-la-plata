from rest_framework import serializers
from core.models import Categoria, Cliente, Inventario, Producto
from django.db import transaction

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'activo']

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'cuit_dni', 'razon_social', 'direccion', 'condicion_iva']

class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventario
        fields = ['stock_fisico', 'stock_reservado']

class ProductoCreateSerializer(serializers.ModelSerializer):
    # stock_inicial solo para crear
    stock_inicial = serializers.IntegerField(write_only=True, default=0)
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    inventario = InventarioSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'codigo_barra', 'nombre', 'descripcion',
            'precio_lista', 'precio_actual', 'tiendanube_id',
            'categoria', 'categoria_nombre', 'activo', 'stock_inicial', 'inventario'
        ]

    def validate_stock_inicial(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock inicial no puede ser negativo.")
        return value

    def create(self, validated_data):
        stock_inicial = validated_data.pop('stock_inicial', 0)
        
        # Transacción atómica: si falla la creación del inventario, se revierte el producto
        with transaction.atomic():
            producto = Producto.objects.create(**validated_data)
            Inventario.objects.create(
                producto=producto,
                stock_fisico=stock_inicial,
                stock_reservado=0
            )
        return producto

class ProductoUpdateSerializer(serializers.ModelSerializer):
    # Sin stock_inicial para proteger el inventario en las actualizaciones (PUT/PATCH)
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    inventario = InventarioSerializer(read_only=True)

    def validate_categoria(self, value):
        if value and not value.activo:
            raise serializers.ValidationError("No se puede asociar un producto a una categoría inactiva.")
        return value

    class Meta:
        model = Producto
        fields = [
            'id', 'codigo_barra', 'nombre', 'descripcion',
            'precio_lista', 'precio_actual', 'tiendanube_id',
            'categoria', 'categoria_nombre', 'activo', 'inventario'
        ]