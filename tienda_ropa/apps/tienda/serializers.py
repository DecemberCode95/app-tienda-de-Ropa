"""
Serializers para la aplicación Tienda de Ropa.

Este módulo contiene todos los serializadores necesarios para convertir
los modelos en representaciones JSON y validar datos de entrada.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import Categoria, Producto, Pedido, Carrito, Resena

Usuario = get_user_model()


class CategoriaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Categoria.
    
    Incluye campos calculados como el número de productos activos.
    """
    numero_productos = serializers.SerializerMethodField(
        read_only=True,
        help_text=_("Número de productos activos en esta categoría")
    )
    
    class Meta:
        model = Categoria
        fields = [
            'id',
            'nombre',
            'descripcion',
            'imagen',
            'activa',
            'fecha_creacion',
            'numero_productos',
        ]
        read_only_fields = ['id', 'fecha_creacion']
    
    def get_numero_productos(self, obj):
        """Retorna el número de productos activos en la categoría."""
        return obj.contar_productos()
    
    def validate_nombre(self, value):
        """Valida que el nombre no esté vacío y tenga longitud adecuada."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError(_("El nombre no puede estar vacío"))
        if len(value) > 100:
            raise serializers.ValidationError(_("El nombre no puede exceder 100 caracteres"))
        return value.strip()


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Producto.
    
    Incluye información completa del producto con campos calculados
    como disponibilidad y promedio de valoración.
    """
    categoria_nombre = serializers.CharField(
        source='categoria.nombre',
        read_only=True,
        help_text=_("Nombre de la categoría")
    )
    disponible = serializers.BooleanField(
        read_only=True,
        help_text=_("Indica si el producto está disponible para compra")
    )
    promedio_valoracion = serializers.FloatField(
        read_only=True,
        allow_null=True,
        help_text=_("Promedio de valoraciones del producto")
    )
    numero_resenas = serializers.SerializerMethodField(
        read_only=True,
        help_text=_("Número total de reseñas")
    )
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'precio',
            'talla',
            'talla_display',
            'stock',
            'categoria',
            'categoria_nombre',
            'imagen',
            'imagenes_adicionales',
            'estado',
            'estado_display',
            'activo',
            'disponible',
            'promedio_valoracion',
            'numero_resenas',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
    
    def get_talla_display(self, obj):
        """Retorna la representación legible de la talla."""
        return obj.get_talla_display()
    
    def get_estado_display(self, obj):
        """Retorna la representación legible del estado."""
        return obj.get_estado_display()
    
    def get_numero_resenas(self, obj):
        """Retorna el número total de reseñas del producto."""
        return obj.resena_set.count()
    
    def validate_precio(self, value):
        """Valida que el precio sea positivo."""
        if value <= 0:
            raise serializers.ValidationError(_("El precio debe ser mayor a cero"))
        return value
    
    def validate_stock(self, value):
        """Valida que el stock no sea negativo."""
        if value < 0:
            raise serializers.ValidationError(_("El stock no puede ser negativo"))
        return value
    
    def validate(self, data):
        """Validaciones adicionales a nivel de objeto."""
        # Si el stock es 0, el estado debería ser 'agotado' o 'descatalogado'
        if data.get('stock', 0) == 0 and data.get('estado') == 'disponible':
            raise serializers.ValidationError({
                'estado': _("Un producto sin stock no puede estar en estado 'disponible'")
            })
        return data


class ProductoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listados de productos.
    
    Usa menos campos para mejorar el rendimiento en listados.
    """
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    disponible = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'precio',
            'talla',
            'stock',
            'categoria_nombre',
            'imagen',
            'estado',
            'disponible',
            'promedio_valoracion',
        ]


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Usuario.
    
    Excluye campos sensibles y proporciona información del perfil.
    """
    tipo_usuario_display = serializers.CharField(
        source='get_tipo_usuario_display',
        read_only=True,
        help_text=_("Tipo de usuario legible")
    )
    es_vip = serializers.BooleanField(read_only=True)
    total_pedidos = serializers.IntegerField(read_only=True)
    gasto_total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        help_text=_("Gasto total del usuario")
    )
    
    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'telefono',
            'fecha_nacimiento',
            'tipo_usuario',
            'tipo_usuario_display',
            'direccion',
            'ciudad',
            'codigo_postal',
            'pais',
            'newsletter',
            'es_vip',
            'total_pedidos',
            'gasto_total',
            'fecha_registro',
            'ultimo_login',
        ]
        read_only_fields = [
            'id', 'fecha_registro', 'ultimo_login',
            'es_vip', 'total_pedidos', 'gasto_total'
        ]
    
    def validate_email(self, value):
        """Valida que el email tenga un formato correcto."""
        if not value or '@' not in value:
            raise serializers.ValidationError(_("Introduce un email válido"))
        return value.lower()
    
    def validate_telefono(self, value):
        """Valida el formato del teléfono si se proporciona."""
        if value:
            # Eliminar espacios y guiones
            limpio = value.replace(' ', '').replace('-', '').replace('+', '')
            if not limpio.isdigit() or len(limpio) < 9 or len(limpio) > 15:
                raise serializers.ValidationError(
                    _("El teléfono debe tener entre 9 y 15 dígitos")
                )
        return value


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de nuevos usuarios.
    
    Incluye validación de contraseña y campos requeridos para registro.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text=_("Contraseña del usuario")
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text=_("Confirmación de contraseña")
    )
    
    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'telefono',
        ]
    
    def validate_username(self, value):
        """Valida que el username tenga longitud adecuada."""
        if len(value) < 3:
            raise serializers.ValidationError(
                _("El nombre de usuario debe tener al menos 3 caracteres")
            )
        if len(value) > 30:
            raise serializers.ValidationError(
                _("El nombre de usuario no puede exceder 30 caracteres")
            )
        return value
    
    def validate_password(self, value):
        """Valida la fortaleza de la contraseña."""
        if len(value) < 8:
            raise serializers.ValidationError(
                _("La contraseña debe tener al menos 8 caracteres")
            )
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError(
                _("La contraseña debe incluir al menos una letra mayúscula")
            )
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError(
                _("La contraseña debe incluir al menos un número")
            )
        return value
    
    def validate(self, data):
        """Valida que las contraseñas coincidan."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': _("Las contraseñas no coinciden")
            })
        
        # Verificar si el email ya existe
        if Usuario.objects.filter(email=data['email'].lower()).exists():
            raise serializers.ValidationError({
                'email': _("Este email ya está registrado")
            })
        
        # Eliminar campo password_confirm antes de guardar
        data.pop('password_confirm')
        return data
    
    def create(self, validated_data):
        """Crea el usuario con contraseña hasheada."""
        validated_data['email'] = validated_data['email'].lower()
        usuario = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            telefono=validated_data.get('telefono', ''),
        )
        return usuario


class PedidoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Pedido.
    
    Incluye información completa del pedido con validaciones.
    """
    usuario_nombre = serializers.CharField(
        source='usuario.username',
        read_only=True,
        help_text=_("Nombre de usuario del cliente")
    )
    usuario_email = serializers.EmailField(
        source='usuario.email',
        read_only=True,
        help_text=_("Email del cliente")
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True,
        help_text=_("Estado legible del pedido")
    )
    metodo_pago_display = serializers.CharField(
        source='get_metodo_pago_display',
        read_only=True,
        help_text=_("Método de pago legible")
    )
    
    class Meta:
        model = Pedido
        fields = [
            'id',
            'usuario',
            'usuario_nombre',
            'usuario_email',
            'productos',
            'subtotal',
            'impuestos',
            'gastos_envio',
            'total',
            'estado',
            'estado_display',
            'metodo_pago',
            'metodo_pago_display',
            'direccion_envio',
            'ciudad_envio',
            'codigo_postal_envio',
            'pais_envio',
            'telefono_contacto',
            'notas',
            'numero_seguimiento',
            'fecha_pedido',
            'fecha_envio',
            'fecha_entrega',
        ]
        read_only_fields = [
            'id', 'usuario', 'usuario_nombre', 'usuario_email',
            'fecha_pedido', 'fecha_envio', 'fecha_entrega',
            'estado_display', 'metodo_pago_display'
        ]
    
    def validate_subtotal(self, value):
        """Valida que el subtotal sea positivo."""
        if value < 0:
            raise serializers.ValidationError(_("El subtotal no puede ser negativo"))
        return value
    
    def validate_total(self, value):
        """Valida que el total sea positivo."""
        if value < 0:
            raise serializers.ValidationError(_("El total no puede ser negativo"))
        return value
    
    def validate_productos(self, value):
        """Valida que la lista de productos no esté vacía."""
        if not value or len(value) == 0:
            raise serializers.ValidationError(_("El pedido debe tener al menos un producto"))
        return value


class CarritoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Carrito.
    
    Incluye campos calculados como total de productos y subtotal.
    """
    usuario_nombre = serializers.CharField(
        source='usuario.username',
        read_only=True
    )
    total_productos = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        help_text=_("Subtotal del carrito")
    )
    
    class Meta:
        model = Carrito
        fields = [
            'id',
            'usuario',
            'usuario_nombre',
            'productos',
            'total_productos',
            'subtotal',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'usuario', 'fecha_creacion', 'fecha_actualizacion']


class CarritoItemSerializer(serializers.Serializer):
    """
    Serializer para agregar/actualizar items en el carrito.
    
    Valida los datos necesarios para modificar el carrito.
    """
    producto_id = serializers.IntegerField(
        required=True,
        help_text=_("ID del producto")
    )
    cantidad = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text=_("Cantidad del producto")
    )
    talla = serializers.ChoiceField(
        choices=Producto.TALLAS,
        required=False,
        default='M',
        help_text=_("Talla del producto")
    )
    
    def validate_producto_id(self, value):
        """Valida que el producto exista y esté disponible."""
        try:
            producto = Producto.objects.get(id=value)
            if not producto.disponible:
                raise serializers.ValidationError(
                    _("Este producto no está disponible actualmente")
                )
            if producto.stock < self.initial_data.get('cantidad', 1):
                raise serializers.ValidationError(
                    _("No hay suficiente stock disponible")
                )
        except Producto.DoesNotExist:
            raise serializers.ValidationError(_("Producto no encontrado"))
        return value


class ResenaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Reseña.
    
    Incluye información del usuario y producto con validaciones.
    """
    usuario_nombre = serializers.CharField(
        source='usuario.username',
        read_only=True,
        help_text=_("Nombre del usuario que escribió la reseña")
    )
    producto_nombre = serializers.CharField(
        source='producto.nombre',
        read_only=True,
        help_text=_("Nombre del producto reseñado")
    )
    producto_imagen = serializers.ImageField(
        source='producto.imagen',
        read_only=True,
        help_text=_("Imagen del producto")
    )
    porcentaje_util = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Resena
        fields = [
            'id',
            'usuario',
            'usuario_nombre',
            'producto',
            'producto_nombre',
            'producto_imagen',
            'calificacion',
            'comentario',
            'titulo',
            'verificada',
            'util',
            'no_util',
            'porcentaje_util',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'id', 'usuario', 'usuario_nombre', 'producto_nombre',
            'producto_imagen', 'verificada', 'util', 'no_util',
            'porcentaje_util', 'fecha_creacion', 'fecha_actualizacion'
        ]
    
    def validate_calificacion(self, value):
        """Valida que la calificación esté entre 1 y 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                _("La calificación debe estar entre 1 y 5 estrellas")
            )
        return value
    
    def validate_comentario(self, value):
        """Valida que el comentario tenga longitud adecuada."""
        if len(value) < 10:
            raise serializers.ValidationError(
                _("El comentario debe tener al menos 10 caracteres")
            )
        if len(value) > 2000:
            raise serializers.ValidationError(
                _("El comentario no puede exceder 2000 caracteres")
            )
        return value
    
    def validate(self, data):
        """Validaciones adicionales."""
        # Verificar si el usuario ya reseñó este producto
        if 'producto' in data:
            existing = Resena.objects.filter(
                usuario=self.context['request'].user,
                producto=data['producto']
            )
            if existing.exists():
                raise serializers.ValidationError(
                    _("Ya has escrito una reseña para este producto")
                )
        return data


class ResenaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para crear reseñas.
    
    Solo incluye los campos necesarios para crear una nueva reseña.
    """
    class Meta:
        model = Resena
        fields = ['producto', 'calificacion', 'comentario', 'titulo']
    
    def validate_calificacion(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                _("La calificación debe estar entre 1 y 5 estrellas")
            )
        return value
    
    def validate_comentario(self, value):
        if len(value) < 10:
            raise serializers.ValidationError(
                _("El comentario debe tener al menos 10 caracteres")
            )
        return value
