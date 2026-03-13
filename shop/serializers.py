from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Categoria, Producto, ItemCarrito, Pedido, ItemPedido, Resena
)

User = get_user_model()

# ============ USUARIO ============
class UsuarioSerializer(serializers.ModelSerializer):
    """Serializador para el modelo de Usuario"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'numero_telefono', 'direccion', 'ciudad', 'codigo_postal',
                  'foto_perfil', 'fecha_nacimiento', 'documento_identidad',
                  'es_vendedor', 'verificado', 'fecha_registro')
        read_only_fields = ('id', 'fecha_registro', 'verificado')

class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear nuevos usuarios"""
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
    
    def validate(self, data):
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        return data
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

# ============ CATEGORIA ============
class CategoriaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo de Categoria"""
    class Meta:
        model = Categoria
        fields = ('id', 'nombre', 'descripcion', 'imagen', 'slug', 
                  'activa', 'fecha_creacion', 'fecha_actualizacion')
        read_only_fields = ('id', 'fecha_creacion', 'fecha_actualizacion')

# ============ PRODUCTO ============
class ProductoListSerializer(serializers.ModelSerializer):
    """Serializador para listar productos (versión ligera)"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    vendedor_nombre = serializers.CharField(source='vendedor.get_full_name', read_only=True)
    
    class Meta:
        model = Producto
        fields = ('id', 'nombre', 'precio', 'categoria', 'categoria_nombre',
                  'stock', 'imagen_principal', 'calificacion_promedio',
                  'num_resenas', 'descuento_porcentaje', 'precio_con_descuento',
                  'vendedor_nombre', 'activo')
        read_only_fields = ('id', 'calificacion_promedio', 'num_resenas')

class ProductoDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado para un producto individual"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    vendedor = UsuarioSerializer(read_only=True)
    resenas = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = ('id', 'nombre', 'descripcion', 'precio', 'categoria', 
                  'categoria_nombre', 'stock', 'talla_disponibles', 
                  'colores_disponibles', 'imagen_principal', 'imagenes_adicionales',
                  'vendedor', 'calificacion_promedio', 'num_resenas', 'resenas',
                  'activo', 'descuento_porcentaje', 'precio_con_descuento',
                  'fecha_creacion', 'fecha_actualizacion')
        read_only_fields = ('id', 'calificacion_promedio', 'num_resenas', 
                           'fecha_creacion', 'fecha_actualizacion')
    
    def get_resenas(self, obj):
        resenas = obj.resenas.all()[:5]  # Últimas 5 reseñas
        return ResenaSerializer(resenas, many=True).data

# ============ CARRITO ============
class ItemCarritoSerializer(serializers.ModelSerializer):
    """Serializador para los items del carrito"""
    producto = ProductoListSerializer(read_only=True)
    producto_id = serializers.IntegerField(write_only=True)
    total_item = serializers.SerializerMethodField()
    
    class Meta:
        model = ItemCarrito
        fields = ('id', 'producto', 'producto_id', 'cantidad', 'talla_seleccionada',
                  'color_seleccionado', 'total_item', 'fecha_agregado')
        read_only_fields = ('id', 'fecha_agregado')
    
    def get_total_item(self, obj):
        return obj.producto.precio_con_descuento * obj.cantidad

# ============ PEDIDO ============
class ItemPedidoSerializer(serializers.ModelSerializer):
    """Serializador para los items dentro de un pedido"""
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = ItemPedido
        fields = ('id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario',
                  'talla', 'color')

class PedidoListSerializer(serializers.ModelSerializer):
    """Serializador para listar pedidos"""
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    total_con_envio = serializers.SerializerMethodField()
    
    class Meta:
        model = Pedido
        fields = ('id', 'numero_pedido', 'usuario_nombre', 'estado', 'total',
                  'costo_envio', 'total_con_envio', 'fecha_pedido')
        read_only_fields = ('id', 'numero_pedido', 'fecha_pedido')
    
    def get_total_con_envio(self, obj):
        return obj.total + obj.impuesto + obj.costo_envio

class PedidoDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado para un pedido individual"""
    usuario = UsuarioSerializer(read_only=True)
    items = ItemPedidoSerializer(many=True, read_only=True)
    total_con_envio = serializers.SerializerMethodField()
    
    class Meta:
        model = Pedido
        fields = ('id', 'numero_pedido', 'usuario', 'estado', 'items', 'total',
                  'impuesto', 'costo_envio', 'total_con_envio', 'direccion_envio',
                  'fecha_pedido', 'fecha_entrega_estimada', 'notas')
        read_only_fields = ('id', 'numero_pedido', 'fecha_pedido')
    
    def get_total_con_envio(self, obj):
        return obj.total + obj.impuesto + obj.costo_envio

# ============ RESENA ============
class ResenaSerializer(serializers.ModelSerializer):
    """Serializador para reseñas de productos"""
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    usuario_avatar = serializers.CharField(source='usuario.foto_perfil', read_only=True)
    
    class Meta:
        model = Resena
        fields = ('id', 'usuario', 'usuario_nombre', 'usuario_avatar', 'producto',
                  'calificacion', 'titulo', 'comentario', 'fotos', 'util_count',
                  'verificada', 'fecha_creacion', 'fecha_actualizacion')
        read_only_fields = ('id', 'usuario', 'util_count', 'verificada',
                           'fecha_creacion', 'fecha_actualizacion')
