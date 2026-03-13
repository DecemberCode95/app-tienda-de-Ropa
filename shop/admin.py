from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto, Usuario, Pedido, ItemPedido, ItemCarrito, Resena

# Registrar Usuario
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """Admin personalizado para usuarios"""
    list_display = ('username', 'email', 'get_nombre_completo', 'es_vendedor', 'verificado', 'fecha_registro')
    list_filter = ('es_vendedor', 'verificado', 'fecha_registro')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('fecha_registro', 'last_login')
    fieldsets = (
        ('Información Básica', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'password')
        }),
        ('Información de Perfil', {
            'fields': ('numero_telefono', 'direccion', 'ciudad', 'codigo_postal', 'foto_perfil', 'fecha_nacimiento', 'documento_identidad')
        }),
        ('Estado', {
            'fields': ('es_vendedor', 'verificado', 'is_active', 'is_staff')
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name()
    get_nombre_completo.short_description = 'Nombre Completo'

# Registrar Categoría
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Admin personalizado para categorías"""
    list_display = ('nombre', 'get_productos_count', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'slug', 'descripcion', 'imagen', 'activa')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_productos_count(self, obj):
        count = obj.productos.count()
        return format_html('<span style="color: #417690; font-weight: bold;">{}</span>', count)
    get_productos_count.short_description = 'Productos'

# Admin en línea para ItemPedido
class ItemPedidoInline(admin.TabularInline):
    """Admin en línea para items de pedido"""
    model = ItemPedido
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'talla', 'color')
    readonly_fields = ('precio_unitario',)

# Registrar Producto
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Admin personalizado para productos"""
    list_display = ('nombre', 'categoria', 'get_precio_formateado', 'stock_display', 'calificacion_promedio', 'activo')
    list_filter = ('categoria', 'activo', 'descuento_porcentaje', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion', 'categoria__nombre')
    readonly_fields = ('calificacion_promedio', 'num_resenas', 'fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'categoria', 'vendedor')
        }),
        ('Precios y Descuentos', {
            'fields': ('precio', 'descuento_porcentaje')
        }),
        ('Inventario', {
            'fields': ('stock', 'talla_disponibles', 'colores_disponibles')
        }),
        ('Imágenes', {
            'fields': ('imagen_principal', 'imagenes_adicionales')
        }),
        ('Calificaciones', {
            'fields': ('calificacion_promedio', 'num_resenas'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_precio_formateado(self, obj):
        return format_html('<span style="color: #155724; font-weight: bold;">${}</span>', obj.precio)
    get_precio_formateado.short_description = 'Precio'
    
    def stock_display(self, obj):
        if obj.stock > 10:
            color = '#28a745'
        elif obj.stock > 0:
            color = '#ffc107'
        else:
            color = '#dc3545'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.stock)
    stock_display.short_description = 'Stock'

# Registrar Pedido
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Admin personalizado para pedidos"""
    list_display = ('numero_pedido', 'usuario', 'get_estado_color', 'total', 'fecha_pedido')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('numero_pedido', 'usuario__username', 'usuario__email')
    readonly_fields = ('numero_pedido', 'fecha_pedido', 'usuario')
    inlines = [ItemPedidoInline]
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'usuario', 'estado')
        }),
        ('Detalles Económicos', {
            'fields': ('total', 'impuesto', 'costo_envio')
        }),
        ('Envío', {
            'fields': ('direccion_envio', 'fecha_entrega_estimada')
        }),
        ('Notas y Fechas', {
            'fields': ('notas', 'fecha_pedido'),
            'classes': ('collapse',)
        }),
    )
    
    def get_estado_color(self, obj):
        colors = {
            'pendiente': '#ffc107',
            'confirmado': '#17a2b8',
            'enviado': '#0069d9',
            'entregado': '#28a745',
            'cancelado': '#dc3545'
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html('<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>', 
                          color, obj.get_estado_display())
    get_estado_color.short_description = 'Estado'

# Registrar Reseña
@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    """Admin personalizado para reseñas"""
    list_display = ('usuario', 'producto', 'get_calificacion_estrellas', 'util_count', 'verificada', 'fecha_creacion')
    list_filter = ('calificacion', 'verificada', 'fecha_creacion')
    search_fields = ('usuario__username', 'producto__nombre', 'comentario')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'usuario')
    fieldsets = (
        ('Información de la Reseña', {
            'fields': ('usuario', 'producto', 'calificacion', 'titulo', 'comentario')
        }),
        ('Contenido Multimedia', {
            'fields': ('fotos',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('verificada', 'util_count')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_calificacion_estrellas(self, obj):
        stars = '★' * obj.calificacion + '☆' * (5 - obj.calificacion)
        return format_html('<span style="color: #ffc107; font-size: 14px;">{}</span>', stars)
    get_calificacion_estrellas.short_description = 'Calificación'

# Registrar ItemCarrito
@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    """Admin personalizado para items del carrito"""
    list_display = ('usuario', 'producto', 'cantidad', 'talla_seleccionada', 'color_seleccionado', 'fecha_agregado')
    list_filter = ('fecha_agregado', 'usuario')
    search_fields = ('usuario__username', 'producto__nombre')
    readonly_fields = ('fecha_agregado', 'usuario')
    fieldsets = (
        ('Detalles del Item', {
            'fields': ('usuario', 'producto', 'cantidad')
        }),
        ('Personalización', {
            'fields': ('talla_seleccionada', 'color_seleccionado')
        }),
        ('Fecha', {
            'fields': ('fecha_agregado',),
            'classes': ('collapse',)
        }),
    )

# Configuración del admin
admin.site.site_header = '🛍️ Tienda de Ropa - Admin'
admin.site.site_title = 'Admin Tienda de Ropa'
admin.site.index_title = 'Bienvenido a la Administración de la Tienda'
