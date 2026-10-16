from rest_framework import serializers
from core.models import Categoria, Cliente, Inventario, Producto
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class PapeleraTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        grupos = list(self.user.groups.values_list('name', flat=True))
        data['role'] = 'Dueno' if 'Dueno' in grupos else grupos[0] if grupos else ''
        return data

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
    precio_venta = serializers.ReadOnlyField()

    class Meta:
        model = Producto
        fields = [
            'id', 'codigo_barra', 'nombre', 'descripcion',
            'precio_actual', 'porcentaje_ganancia', 'precio_venta', 'tiendanube_id',
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
    stock_fisico = serializers.IntegerField(write_only=True, required=False, min_value=0)
    precio_venta = serializers.ReadOnlyField()

    def validate_categoria(self, value):
        if value and not value.activo:
            raise serializers.ValidationError("No se puede asociar un producto a una categoría inactiva.")
        return value

    class Meta:
        model = Producto
        fields = [
            'id', 'codigo_barra', 'nombre', 'descripcion',
            'precio_actual', 'porcentaje_ganancia', 'precio_venta', 'tiendanube_id',
            'categoria', 'categoria_nombre', 'activo', 'inventario', 'stock_fisico'
        ]

    def update(self, instance, validated_data):
        stock_fisico = validated_data.pop('stock_fisico', None)
        instance = super().update(instance, validated_data)
        if stock_fisico is not None:
            Inventario.objects.update_or_create(
                producto=instance,
                defaults={'stock_fisico': stock_fisico}
            )
        return instance