"""
Models para la aplicación Tienda de Ropa.

Este módulo define todos los modelos necesarios para gestionar:
- Categorías de productos
- Productos con tallas y stock
- Usuarios personalizados
- Pedidos y su estado
- Carritos de compra
- Reseñas y valoraciones
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Categoria(models.Model):
    """
    Modelo para las categorías de productos.
    
    Permite organizar los productos en categorías jerárquicas
    (ej: Hombre, Mujer, Niños, Accesorios).
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Nombre"),
        help_text=_("Nombre de la categoría")
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name=_("Descripción"),
        help_text=_("Descripción detallada de la categoría")
    )
    imagen = models.ImageField(
        upload_to='categorias/',
        blank=True,
        null=True,
        verbose_name=_("Imagen"),
        help_text=_("Imagen representativa de la categoría")
    )
    activa = models.BooleanField(
        default=True,
        verbose_name=_("Activa"),
        help_text=_("Indica si la categoría está activa y visible")
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de creación")
    )
    
    class Meta:
        verbose_name = _("Categoría")
        verbose_name_plural = _("Categorías")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def contar_productos(self):
        """Retorna el número de productos activos en esta categoría."""
        return self.producto_set.filter(stock__gt=0, activo=True).count()


class Producto(models.Model):
    """
    Modelo para los productos de la tienda.
    
    Incluye información completa del producto: precio, tallas, stock,
    categoría y validaciones para asegurar datos consistentes.
    """
    # Tallas disponibles para ropa
    TALLAS = [
        ('XS', 'Extra Pequeña'),
        ('S', 'Pequeña'),
        ('M', 'Mediana'),
        ('L', 'Grande'),
        ('XL', 'Extra Grande'),
        ('XXL', 'Doble Extra Grande'),
        ('XXXL', 'Triple Extra Grande'),
    ]
    
    # Estados del producto
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('agotado', 'Agotado'),
        ('proximamente', 'Próximamente'),
        ('descatalogado', 'Descatalogado'),
    ]
    
    nombre = models.CharField(
        max_length=200,
        verbose_name=_("Nombre"),
        help_text=_("Nombre del producto")
    )
    descripcion = models.TextField(
        verbose_name=_("Descripción"),
        help_text=_("Descripción detallada del producto")
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name=_("Precio"),
        help_text=_("Precio del producto en euros")
    )
    talla = models.CharField(
        max_length=5,
        choices=TALLAS,
        default='M',
        verbose_name=_("Talla"),
        help_text=_("Talla del producto")
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Stock"),
        help_text=_("Cantidad disponible en inventario")
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='producto_set',
        verbose_name=_("Categoría"),
        help_text=_("Categoría a la que pertenece el producto")
    )
    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        verbose_name=_("Imagen"),
        help_text=_("Imagen principal del producto")
    )
    imagenes_adicionales = models.JSONField(
        blank=True,
        null=True,
        default=list,
        verbose_name=_("Imágenes adicionales"),
        help_text=_("Lista de URLs de imágenes adicionales")
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='disponible',
        verbose_name=_("Estado"),
        help_text=_("Estado actual del producto")
    )
    activo = models.BooleanField(
        default=True,
        verbose_name=_("Activo"),
        help_text=_("Indica si el producto está activo y visible en la tienda")
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de creación")
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Fecha de actualización")
    )
    
    class Meta:
        verbose_name = _("Producto")
        verbose_name_plural = _("Productos")
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['categoria', 'activo']),
            models.Index(fields=['estado']),
            models.Index(fields=['precio']),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.get_talla_display()})"
    
    @property
    def disponible(self):
        """Indica si el producto está disponible para compra."""
        return self.activo and self.stock > 0 and self.estado == 'disponible'
    
    @property
    def promedio_valoracion(self):
        """Calcula el promedio de valoraciones del producto."""
        resenas = self.resena_set.filter(calificacion__isnull=False)
        if resenas.exists():
            return resenas.aggregate(models.Avg('calificacion'))['calificacion__avg']
        return None
    
    def reducir_stock(self, cantidad):
        """Reduce el stock del producto en la cantidad especificada."""
        if cantidad > self.stock:
            raise ValueError(_("No hay suficiente stock disponible"))
        self.stock -= cantidad
        if self.stock == 0:
            self.estado = 'agotado'
        self.save()
    
    def aumentar_stock(self, cantidad):
        """Aumenta el stock del producto en la cantidad especificada."""
        self.stock += cantidad
        if self.stock > 0 and self.estado == 'agotado':
            self.estado = 'disponible'
        self.save()


class Usuario(AbstractUser):
    """
    Modelo personalizado de usuario que extiende AbstractUser.
    
    Añade campos adicionales para gestión de perfiles de clientes,
    direcciones y preferencias.
    """
    # Tipos de usuario
    TIPO_USUARIO = [
        ('cliente', 'Cliente'),
        ('vip', 'Cliente VIP'),
        ('admin', 'Administrador'),
    ]
    
    email = models.EmailField(
        unique=True,
        verbose_name=_("Correo electrónico"),
        help_text=_("Correo electrónico único del usuario")
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_("Teléfono"),
        help_text=_("Número de teléfono del usuario")
    )
    fecha_nacimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Fecha de nacimiento"),
        help_text=_("Fecha de nacimiento del usuario")
    )
    tipo_usuario = models.CharField(
        max_length=10,
        choices=TIPO_USUARIO,
        default='cliente',
        verbose_name=_("Tipo de usuario"),
        help_text=_("Tipo o categoría del usuario")
    )
    direccion = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Dirección"),
        help_text=_("Dirección principal del usuario")
    )
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Ciudad"),
        help_text=_("Ciudad de residencia")
    )
    codigo_postal = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("Código postal"),
        help_text=_("Código postal")
    )
    pais = models.CharField(
        max_length=100,
        default='España',
        verbose_name=_("País"),
        help_text=_("País de residencia")
    )
    newsletter = models.BooleanField(
        default=False,
        verbose_name=_("Suscribirse al newsletter"),
        help_text=_("Indica si el usuario desea recibir el newsletter")
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de registro")
    )
    ultimo_login = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Último login")
    )
    
    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    @property
    def es_vip(self):
        """Indica si el usuario es VIP."""
        return self.tipo_usuario == 'vip'
    
    @property
    def total_pedidos(self):
        """Retorna el número total de pedidos del usuario."""
        return self.pedido_set.count()
    
    @property
    def gasto_total(self):
        """Calcula el gasto total del usuario en todos sus pedidos."""
        total = self.pedido_set.filter(estado='entregado').aggregate(
            total=models.Sum('total')
        )['total']
        return total or 0.00


class Pedido(models.Model):
    """
    Modelo para gestionar los pedidos de los usuarios.
    
    Almacena información completa del pedido incluyendo productos,
    totales, estado y fechas de seguimiento.
    """
    # Estados posibles del pedido
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('preparando', 'Preparando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
        ('reembolsado', 'Reembolsado'),
    ]
    
    # Métodos de pago
    METODOS_PAGO = [
        ('tarjeta', 'Tarjeta de crédito/débito'),
        ('paypal', 'PayPal'),
        ('transferencia', 'Transferencia bancaria'),
        ('contrareembolso', 'Contra reembolso'),
    ]
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='pedido_set',
        verbose_name=_("Usuario"),
        help_text=_("Usuario que realizó el pedido")
    )
    productos = models.JSONField(
        verbose_name=_("Productos"),
        help_text=_("Lista de productos del pedido con cantidades y precios")
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Subtotal"),
        help_text=_("Subtotal antes de impuestos y envío")
    )
    impuestos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        verbose_name=_("Impuestos"),
        help_text=_("Impuestos aplicados (IVA)")
    )
    gastos_envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        verbose_name=_("Gastos de envío"),
        help_text=_("Coste de envío")
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Total"),
        help_text=_("Total final del pedido")
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='pendiente',
        verbose_name=_("Estado"),
        help_text=_("Estado actual del pedido")
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS_PAGO,
        default='tarjeta',
        verbose_name=_("Método de pago"),
        help_text=_("Método de pago utilizado")
    )
    direccion_envio = models.CharField(
        max_length=255,
        verbose_name=_("Dirección de envío"),
        help_text=_("Dirección donde se enviará el pedido")
    )
    ciudad_envio = models.CharField(
        max_length=100,
        verbose_name=_("Ciudad de envío"),
        help_text=_("Ciudad de envío")
    )
    codigo_postal_envio = models.CharField(
        max_length=10,
        verbose_name=_("Código postal de envío"),
        help_text=_("Código postal de envío")
    )
    pais_envio = models.CharField(
        max_length=100,
        default='España',
        verbose_name=_("País de envío"),
        help_text=_("País de envío")
    )
    telefono_contacto = models.CharField(
        max_length=15,
        verbose_name=_("Teléfono de contacto"),
        help_text=_("Teléfono para contactar sobre el pedido")
    )
    notas = models.TextField(
        blank=True,
        verbose_name=_("Notas"),
        help_text=_("Notas adicionales del pedido")
    )
    numero_seguimiento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Número de seguimiento"),
        help_text=_("Número de seguimiento del envío")
    )
    fecha_pedido = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha del pedido")
    )
    fecha_envio = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Fecha de envío")
    )
    fecha_entrega = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Fecha de entrega")
    )
    
    class Meta:
        verbose_name = _("Pedido")
        verbose_name_plural = _("Pedidos")
        ordering = ['-fecha_pedido']
        indexes = [
            models.Index(fields=['usuario', 'estado']),
            models.Index(fields=['fecha_pedido']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"
    
    def calcular_total(self):
        """Calcula el total del pedido incluyendo subtotal, impuestos y envío."""
        self.total = self.subtotal + self.impuestos + self.gastos_envio
        return self.total
    
    def cancelar(self):
        """Cambia el estado del pedido a cancelado."""
        if self.estado in ['entregado', 'reembolsado']:
            raise ValueError(_("No se puede cancelar un pedido ya entregado o reembolsado"))
        self.estado = 'cancelado'
        self.save()
    
    def marcar_enviado(self, numero_seguimiento=None):
        """Marca el pedido como enviado."""
        if self.estado not in ['pendiente', 'confirmado', 'preparando']:
            raise ValueError(_("El pedido no está en estado válido para envío"))
        self.estado = 'enviado'
        self.fecha_envio = timezone.now()
        if numero_seguimiento:
            self.numero_seguimiento = numero_seguimiento
        self.save()
    
    def marcar_entregado(self):
        """Marca el pedido como entregado."""
        if self.estado != 'enviado':
            raise ValueError(_("Solo se pueden marcar como entregados los pedidos enviados"))
        self.estado = 'entregado'
        self.fecha_entrega = timezone.now()
        self.save()


class Carrito(models.Model):
    """
    Modelo para gestionar el carrito de compras de los usuarios.
    
    Permite almacenar productos temporalmente antes de finalizar la compra.
    """
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='carrito',
        verbose_name=_("Usuario"),
        help_text=_("Usuario propietario del carrito")
    )
    productos = models.JSONField(
        default=list,
        verbose_name=_("Productos"),
        help_text=_("Lista de productos en el carrito con cantidades")
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de creación")
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Fecha de actualización")
    )
    
    class Meta:
        verbose_name = _("Carrito")
        verbose_name_plural = _("Carritos")
    
    def __str__(self):
        return f"Carrito de {self.usuario.username}"
    
    @property
    def total_productos(self):
        """Retorna el número total de productos en el carrito."""
        return sum(item.get('cantidad', 0) for item in self.productos)
    
    @property
    def subtotal(self):
        """Calcula el subtotal del carrito."""
        return sum(
            item.get('precio', 0) * item.get('cantidad', 0)
            for item in self.productos
        )
    
    def agregar_producto(self, producto_id, cantidad=1, precio=None, nombre=None, talla=None):
        """
        Agrega un producto al carrito o aumenta su cantidad si ya existe.
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad a agregar
            precio: Precio unitario del producto
            nombre: Nombre del producto
            talla: Talla del producto
        """
        for item in self.productos:
            if item['producto_id'] == producto_id and item.get('talla') == talla:
                item['cantidad'] += cantidad
                self.fecha_actualizacion = timezone.now()
                self.save()
                return
        
        # Producto no existe en el carrito, lo agregamos
        self.productos.append({
            'producto_id': producto_id,
            'cantidad': cantidad,
            'precio': precio or 0,
            'nombre': nombre or '',
            'talla': talla,
        })
        self.fecha_actualizacion = timezone.now()
        self.save()
    
    def eliminar_producto(self, producto_id, talla=None):
        """
        Elimina un producto del carrito.
        
        Args:
            producto_id: ID del producto a eliminar
            talla: Talla del producto (opcional, para diferenciar variantes)
        """
        self.productos = [
            item for item in self.productos
            if not (item['producto_id'] == producto_id and item.get('talla') == talla)
        ]
        self.fecha_actualizacion = timezone.now()
        self.save()
    
    def actualizar_cantidad(self, producto_id, cantidad, talla=None):
        """
        Actualiza la cantidad de un producto en el carrito.
        
        Args:
            producto_id: ID del producto
            cantidad: Nueva cantidad (si es 0 o menor, se elimina el producto)
            talla: Talla del producto
        """
        if cantidad <= 0:
            self.eliminar_producto(producto_id, talla)
            return
        
        for item in self.productos:
            if item['producto_id'] == producto_id and item.get('talla') == talla:
                item['cantidad'] = cantidad
                self.fecha_actualizacion = timezone.now()
                self.save()
                return
        
        raise ValueError(_("Producto no encontrado en el carrito"))
    
    def vaciar(self):
        """Vacía completamente el carrito."""
        self.productos = []
        self.fecha_actualizacion = timezone.now()
        self.save()


class Resena(models.Model):
    """
    Modelo para las reseñas y valoraciones de productos.
    
    Permite a los usuarios calificar y comentar sobre los productos
    que han comprado.
    """
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='resena_set',
        verbose_name=_("Usuario"),
        help_text=_("Usuario que escribió la reseña")
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='resena_set',
        verbose_name=_("Producto"),
        help_text=_("Producto reseñado")
    )
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Calificación"),
        help_text=_("Calificación de 1 a 5 estrellas")
    )
    comentario = models.TextField(
        verbose_name=_("Comentario"),
        help_text=_("Comentario detallado sobre el producto")
    )
    titulo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Título"),
        help_text=_("Título resumido de la reseña")
    )
    verificada = models.BooleanField(
        default=False,
        verbose_name=_("Compra verificada"),
        help_text=_("Indica si la reseña es de una compra verificada")
    )
    util = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Útil"),
        help_text=_("Número de usuarios que marcaron la reseña como útil")
    )
    no_util = models.PositiveIntegerField(
        default=0,
        verbose_name=_("No útil"),
        help_text=_("Número de usuarios que marcaron la reseña como no útil")
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de creación")
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Fecha de actualización")
    )
    
    class Meta:
        verbose_name = _("Reseña")
        verbose_name_plural = _("Reseñas")
        ordering = ['-fecha_creacion']
        unique_together = [['usuario', 'producto']]
        indexes = [
            models.Index(fields=['producto', 'calificacion']),
            models.Index(fields=['verificada']),
        ]
    
    def __str__(self):
        return f"{self.calificacion}★ - {self.producto.nombre} por {self.usuario.username}"
    
    @property
    def porcentaje_util(self):
        """Calcula el porcentaje de votos útiles."""
        total_votos = self.util + self.no_util
        if total_votos == 0:
            return 0
        return round((self.util / total_votos) * 100, 2)


# Import necesario para referencias forward en models
from django.utils import timezone
