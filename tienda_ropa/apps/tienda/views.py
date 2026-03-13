"""
Views para la aplicación Tienda de Ropa.

Este módulo contiene los ViewSets REST para gestionar todos los modelos
con operaciones CRUD completas, filtrado, búsqueda y paginación.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.exceptions import NotFound, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q
from django.utils.translation import gettext_lazy as _

from .models import Categoria, Producto, Usuario, Pedido, Carrito, Resena
from .serializers import (
    CategoriaSerializer,
    ProductoSerializer,
    ProductoListSerializer,
    UsuarioSerializer,
    UsuarioRegistroSerializer,
    PedidoSerializer,
    CarritoSerializer,
    CarritoItemSerializer,
    ResenaSerializer,
    ResenaCreateSerializer,
)


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar categorías de productos.
    
    Endpoints disponibles:
    - GET /api/categorias/ - Listar todas las categorías
    - GET /api/categorias/{id}/ - Obtener detalle de una categoría
    - POST /api/categorias/ - Crear nueva categoría (admin)
    - PUT /api/categorias/{id}/ - Actualizar categoría (admin)
    - DELETE /api/categorias/{id}/ - Eliminar categoría (admin)
    - GET /api/categorias/activas/ - Listar categorías activas
    - GET /api/categorias/{id}/productos/ - Listar productos de una categoría
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]  # Lectura pública, escritura solo admin
    
    def get_permissions(self):
        """Personaliza permisos según la acción."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]
    
    def get_queryset(self):
        """Filtra categorías según parámetros de búsqueda."""
        queryset = Categoria.objects.all()
        
        # Filtrar por estado activo
        activa = self.request.query_params.get('activa')
        if activa is not None:
            queryset = queryset.filter(activa=activa.lower() == 'true')
        
        # Búsqueda por nombre o descripción
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Retorna solo las categorías activas."""
        categorias_activas = self.get_queryset().filter(activa=True)
        serializer = self.get_serializer(categorias_activas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def productos(self, request, pk=None):
        """Retorna todos los productos de una categoría específica."""
        categoria = self.get_object()
        productos = categoria.producto_set.filter(activo=True)
        
        # Aplicar filtros adicionales
        disponible = request.query_params.get('disponible')
        if disponible is not None:
            productos = productos.filter(stock__gt=0)
        
        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)


class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar productos de la tienda.
    
    Endpoints disponibles:
    - GET /api/productos/ - Listar productos (con filtros y paginación)
    - GET /api/productos/{id}/ - Obtener detalle de un producto
    - POST /api/productos/ - Crear nuevo producto (admin)
    - PUT /api/productos/{id}/ - Actualizar producto (admin)
    - DELETE /api/productos/{id}/ - Eliminar producto (admin)
    - GET /api/productos/disponibles/ - Listar productos disponibles
    - GET /api/productos/ofertas/ - Listar productos en oferta
    - GET /api/productos/mas-vendidos/ - Listar productos más vendidos
    - POST /api/productos/{id}/resenas/ - Añadir reseña a producto
    """
    queryset = Producto.objects.select_related('categoria').all()
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion', 'categoria__nombre']
    ordering_fields = ['precio', 'stock', 'fecha_creacion', 'nombre']
    
    def get_serializer_class(self):
        """Usa serializer simplificado para listados."""
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoSerializer
    
    def get_permissions(self):
        """Personaliza permisos según la acción."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]
    
    def get_queryset(self):
        """Filtra productos según parámetros de búsqueda."""
        queryset = Producto.objects.select_related('categoria').all()
        
        # Filtrar por categoría
        categoria = self.request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        
        # Filtrar por talla
        talla = self.request.query_params.get('talla')
        if talla:
            queryset = queryset.filter(talla=talla)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por disponibilidad
        disponible = self.request.query_params.get('disponible')
        if disponible is not None and disponible.lower() == 'true':
            queryset = queryset.filter(stock__gt=0, activo=True, estado='disponible')
        
        # Filtrar por rango de precios
        precio_min = self.request.query_params.get('precio_min')
        precio_max = self.request.query_params.get('precio_max')
        if precio_min:
            queryset = queryset.filter(precio__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(precio__lte=precio_max)
        
        # Filtrar por promedio de valoración
        valoracion_min = self.request.query_params.get('valoracion_min')
        if valoracion_min:
            queryset = queryset.annotate(
                avg_rating=Avg('resena__calificacion')
            ).filter(avg_rating__gte=float(valoracion_min))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """Retorna solo los productos disponibles para compra."""
        productos = self.get_queryset().filter(
            stock__gt=0,
            activo=True,
            estado='disponible'
        )
        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def ofertas(self, request):
        """Retorna productos en oferta (ejemplo: precio menor a cierto valor)."""
        # Esto es un ejemplo, se podría implementar lógica real de ofertas
        productos = self.get_queryset().filter(
            activo=True,
            stock__gt=0
        ).order_by('precio')[:10]  # Los 10 más baratos como "oferta"
        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mas_vendidos(self, request):
        """Retorna los productos más vendidos (basado en pedidos)."""
        # Nota: En producción esto se optimizaría con caché
        productos = Producto.objects.filter(
            activo=True,
            resena__isnull=False
        ).annotate(
            num_resenas=Count('resena')
        ).order_by('-num_resenas')[:10]
        
        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def resenas(self, request, pk=None):
        """Añade una reseña al producto."""
        producto = self.get_object()
        
        # Verificar si el usuario ya reseñó este producto
        if Resena.objects.filter(usuario=request.user, producto=producto).exists():
            return Response(
                {'error': _('Ya has escrito una reseña para este producto')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ResenaCreateSerializer(data=request.data)
        if serializer.is_valid():
            resena = serializer.save(
                usuario=request.user,
                producto=producto,
                verificada=self._verificar_compra(request.user, producto)
            )
            return Response(ResenaSerializer(resena).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _verificar_compra(self, usuario, producto):
        """Verifica si el usuario ha comprado el producto anteriormente."""
        return Pedido.objects.filter(
            usuario=usuario,
            estado='entregado',
            productos__contains=[{'producto_id': producto.id}]
        ).exists()


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios.
    
    Endpoints disponibles:
    - GET /api/usuarios/ - Listar usuarios (admin)
    - GET /api/usuarios/{id}/ - Obtener detalle de usuario
    - PUT /api/usuarios/{id}/ - Actualizar usuario
    - GET /api/usuarios/perfil/ - Obtener perfil del usuario actual
    - PUT /api/usuarios/perfil/ - Actualizar perfil del usuario actual
    - GET /api/usuarios/mis-pedidos/ - Obtener pedidos del usuario actual
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Personaliza permisos según la acción."""
        if self.action in ['list', 'retrieve_admin']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Solo admins pueden ver todos los usuarios."""
        if self.request.user.is_staff:
            return Usuario.objects.all()
        return Usuario.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def perfil(self, request):
        """Gestiona el perfil del usuario autenticado."""
        usuario = request.user
        
        if request.method == 'GET':
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(
                usuario,
                data=request.data,
                partial=partial
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def mis_pedidos(self, request):
        """Retorna los pedidos del usuario autenticado."""
        pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Retorna estadísticas del usuario (solo para el propio usuario o admin)."""
        usuario = request.user
        
        stats = {
            'total_pedidos': usuario.total_pedidos,
            'gasto_total': float(usuario.gasto_total),
            'es_vip': usuario.es_vip,
            'productos_reseñados': usuario.resena_set.count(),
            'calificacion_promedio': usuario.resena_set.aggregate(
                Avg('calificacion')
            )['calificacion__avg'] or 0,
        }
        
        return Response(stats)


class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pedidos.
    
    Endpoints disponibles:
    - GET /api/pedidos/ - Listar pedidos (admin)
    - GET /api/pedidos/{id}/ - Obtener detalle de pedido
    - POST /api/pedidos/ - Crear nuevo pedido
    - PUT /api/pedidos/{id}/ - Actualizar pedido (admin)
    - GET /api/pedidos/mis-pedidos/ - Pedidos del usuario actual
    - POST /api/pedidos/{id}/cancelar/ - Cancelar pedido
    - POST /api/pedidos/{id}/enviar/ - Marcar como enviado (admin)
    - POST /api/pedidos/{id}/entregar/ - Marcar como entregado (admin)
    """
    queryset = Pedido.objects.select_related('usuario').all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha_pedido', 'total', 'estado']
    
    def get_permissions(self):
        """Personaliza permisos según la acción."""
        if self.action in ['create', 'mis_pedidos', 'cancelar_pedido']:
            return [IsAuthenticated()]
        elif self.action in ['list', 'update', 'partial_update', 'enviar_pedido', 'entregar_pedido']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filtra pedidos según el usuario (no admin ve solo los suyos)."""
        if self.request.user.is_staff:
            return Pedido.objects.select_related('usuario').all()
        return Pedido.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        """Asigna el usuario autenticado al pedido."""
        serializer.save(usuario=self.request.user)
    
    @action(detail=False, methods=['get'])
    def mis_pedidos(self, request):
        """Retorna los pedidos del usuario autenticado."""
        pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
        serializer = self.get_serializer(pedidos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancelar(self, request, pk=None):
        """Cancela un pedido (solo si está en estado válido)."""
        pedido = self.get_object()
        
        # Verificar permisos
        if not request.user.is_staff and pedido.usuario != request.user:
            raise PermissionDenied(_("No tienes permiso para cancelar este pedido"))
        
        try:
            pedido.cancelar()
            return Response({
                'mensaje': _('Pedido cancelado exitosamente'),
                'estado': pedido.estado
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser()])
    def enviar(self, request, pk=None):
        """Marca un pedido como enviado (solo admin)."""
        pedido = self.get_object()
        numero_seguimiento = request.data.get('numero_seguimiento')
        
        try:
            pedido.marcar_enviado(numero_seguimiento)
            return Response({
                'mensaje': _('Pedido marcado como enviado'),
                'estado': pedido.estado,
                'fecha_envio': pedido.fecha_envio,
                'numero_seguimiento': pedido.numero_seguimiento
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser()])
    def entregar(self, request, pk=None):
        """Marca un pedido como entregado (solo admin)."""
        pedido = self.get_object()
        
        try:
            pedido.marcar_entregado()
            return Response({
                'mensaje': _('Pedido marcado como entregado'),
                'estado': pedido.estado,
                'fecha_entrega': pedido.fecha_entrega
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CarritoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar carritos de compra.
    
    Endpoints disponibles:
    - GET /api/carrito/ - Obtener carrito del usuario actual
    - POST /api/carrito/agregar/ - Agregar producto al carrito
    - POST /api/carrito/actualizar/ - Actualizar cantidad de producto
    - DELETE /api/carrito/eliminar/ - Eliminar producto del carrito
    - DELETE /api/carrito/vaciar/ - Vaciar carrito completo
    """
    serializer_class = CarritoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna solo el carrito del usuario autenticado."""
        return Carrito.objects.filter(usuario=self.request.user)
    
    def get_object(self):
        """Obtiene o crea el carrito del usuario autenticado."""
        carrito, created = Carrito.objects.get_or_create(
            usuario=self.request.user,
            defaults={'productos': []}
        )
        return carrito
    
    @action(detail=False, methods=['post'])
    def agregar(self, request):
        """Agrega un producto al carrito."""
        serializer = CarritoItemSerializer(data=request.data)
        if serializer.is_valid():
            carrito = self.get_object()
            producto_data = serializer.validated_data
            
            # Obtener producto para obtener precio y nombre
            producto = get_object_or_404(Producto, id=producto_data['producto_id'])
            
            carrito.agregar_producto(
                producto_id=producto.id,
                cantidad=producto_data['cantidad'],
                precio=float(producto.precio),
                nombre=producto.nombre,
                talla=producto_data.get('talla', 'M')
            )
            
            return Response(CarritoSerializer(carrito).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def actualizar(self, request):
        """Actualiza la cantidad de un producto en el carrito."""
        producto_id = request.data.get('producto_id')
        cantidad = request.data.get('cantidad')
        talla = request.data.get('talla', 'M')
        
        if not producto_id or cantidad is None:
            return Response(
                {'error': _('Se requiere producto_id y cantidad')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        carrito = self.get_object()
        
        try:
            carrito.actualizar_cantidad(
                producto_id=int(producto_id),
                cantidad=int(cantidad),
                talla=talla
            )
            return Response(CarritoSerializer(carrito).data)
        except (ValueError, KeyError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def eliminar(self, request):
        """Elimina un producto del carrito."""
        producto_id = request.query_params.get('producto_id')
        talla = request.query_params.get('talla', 'M')
        
        if not producto_id:
            return Response(
                {'error': _('Se requiere producto_id')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        carrito = self.get_object()
        carrito.eliminar_producto(int(producto_id), talla)
        
        return Response(CarritoSerializer(carrito).data)
    
    @action(detail=False, methods=['delete'])
    def vaciar(self, request):
        """Vacía completamente el carrito."""
        carrito = self.get_object()
        carrito.vaciar()
        
        return Response({
            'mensaje': _('Carrito vaciado exitosamente'),
            'carrito': CarritoSerializer(carrito).data
        })


class ResenaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reseñas de productos.
    
    Endpoints disponibles:
    - GET /api/resenas/ - Listar todas las reseñas
    - GET /api/resenas/{id}/ - Obtener detalle de reseña
    - POST /api/resenas/ - Crear nueva reseña (usuario autenticado)
    - PUT /api/resenas/{id}/ - Actualizar reseña (solo autor)
    - DELETE /api/resenas/{id}/ - Eliminar reseña (autor o admin)
    - GET /api/resenas/producto/{producto_id}/ - Reseñas de un producto
    - POST /api/resenas/{id}/votar/ - Votar reseña como útil/no útil
    """
    queryset = Resena.objects.select_related('usuario', 'producto').all()
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha_creacion', 'calificacion', 'util']
    
    def get_serializer_class(self):
        """Usa serializer apropiado según la acción."""
        if self.action == 'create':
            return ResenaCreateSerializer
        return ResenaSerializer
    
    def get_permissions(self):
        """Personaliza permisos según la acción."""
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_queryset(self):
        """Filtra reseñas según parámetros."""
        queryset = Resena.objects.select_related('usuario', 'producto').all()
        
        # Filtrar por producto
        producto = self.request.query_params.get('producto')
        if producto:
            queryset = queryset.filter(producto_id=producto)
        
        # Filtrar por calificación mínima
        calificacion_min = self.request.query_params.get('calificacion_min')
        if calificacion_min:
            queryset = queryset.filter(calificacion__gte=int(calificacion_min))
        
        # Filtrar por compras verificadas
        verificada = self.request.query_params.get('verificada')
        if verificada is not None:
            queryset = queryset.filter(verificada=verificada.lower() == 'true')
        
        return queryset
    
    def perform_create(self, serializer):
        """Crea la reseña asignando usuario y verificando compra."""
        producto_id = self.request.data.get('producto')
        producto = get_object_or_404(Producto, id=producto_id)
        
        # Verificar si ya existe reseña de este usuario para este producto
        if Resena.objects.filter(usuario=self.request.user, producto=producto).exists():
            raise serializers.ValidationError(
                _('Ya has escrito una reseña para este producto')
            )
        
        serializer.save(
            usuario=self.request.user,
            producto=producto,
            verificada=self._verificar_compra(self.request.user, producto)
        )
    
    def perform_update(self, serializer):
        """Actualiza solo si el usuario es el autor."""
        resena = self.get_object()
        if resena.usuario != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied(_("Solo puedes editar tus propias reseñas"))
        serializer.save()
    
    def perform_destroy(self, instance):
        """Elimina solo si el usuario es el autor o admin."""
        if instance.usuario != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied(_("Solo puedes eliminar tus propias reseñas"))
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def producto(self, request, producto_id=None):
        """Retorna todas las reseñas de un producto específico."""
        resenas = Resena.objects.filter(producto_id=producto_id).order_by('-fecha_creacion')
        serializer = self.get_serializer(resenas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def votar(self, request, pk=None):
        """Permite votar una reseña como útil o no útil."""
        resena = self.get_object()
        voto = request.data.get('voto')
        
        if voto not in ['util', 'no_util']:
            return Response(
                {'error': _('El voto debe ser "util" o "no_util"')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Evitar que el autor vote su propia reseña
        if resena.usuario == request.user:
            return Response(
                {'error': _('No puedes votar tu propia reseña')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if voto == 'util':
            resena.util += 1
        else:
            resena.no_util += 1
        
        resena.save()
        
        return Response({
            'mensaje': _('Voto registrado exitosamente'),
            'util': resena.util,
            'no_util': resena.no_util,
            'porcentaje_util': resena.porcentaje_util
        })
    
    def _verificar_compra(self, usuario, producto):
        """Verifica si el usuario ha comprado el producto."""
        return Pedido.objects.filter(
            usuario=usuario,
            estado='entregado',
            productos__contains=[{'producto_id': producto.id}]
        ).exists()


# Import necesario para referencias forward
from rest_framework import serializers
