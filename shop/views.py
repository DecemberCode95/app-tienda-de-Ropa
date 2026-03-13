from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Categoria, Producto, ItemCarrito, Pedido, ItemPedido, Resena
from .serializers import (
    UsuarioSerializer, UsuarioCreateSerializer, CategoriaSerializer,
    ProductoListSerializer, ProductoDetailSerializer, ItemCarritoSerializer,
    PedidoListSerializer, PedidoDetailSerializer, ResenaSerializer
)

User = get_user_model()

# ============ USUARIO ============
class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de usuarios"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Obtener perfil del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_password(self, request, pk=None):
        """Cambiar contraseña del usuario"""
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response({"error": "No tienes permiso"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UsuarioSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            if 'password' in request.data:
                user.set_password(request.data['password'])
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============ CATEGORIA ============
class CategoriaViewSet(viewsets.ModelViewSet):
    """ViewSet para categorías de productos"""
    queryset = Categoria.objects.filter(activa=True)
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'fecha_creacion']
    ordering = ['nombre']

# ============ PRODUCTO ============
class ProductoViewSet(viewsets.ModelViewSet):
    """ViewSet para productos de la tienda"""
    queryset = Producto.objects.filter(activo=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'stock', 'descuento_porcentaje']
    search_fields = ['nombre', 'descripcion', 'categoria__nombre']
    ordering_fields = ['precio', 'calificacion_promedio', 'fecha_creacion']
    ordering = ['-fecha_creacion']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductoDetailSerializer
        return ProductoListSerializer
    
    def perform_create(self, serializer):
        """Asignar vendedor al crear producto"""
        serializer.save(vendedor=self.request.user)
    
    @action(detail=True, methods=['get'])
    def resenas(self, request, pk=None):
        """Obtener reseñas de un producto"""
        producto = self.get_object()
        resenas = producto.resenas.all()
        serializer = ResenaSerializer(resenas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def resena_crear(self, request, pk=None):
        """Crear o actualizar reseña de un producto"""
        producto = self.get_object()
        resena, created = Resena.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults=request.data
        )
        if not created:
            for attr, value in request.data.items():
                setattr(resena, attr, value)
            resena.save()
        
        serializer = ResenaSerializer(resena)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

# ============ CARRITO ============
class CarritoViewSet(viewsets.ViewSet):
    """ViewSet para carrito de compras"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Obtener carrito del usuario"""
        items = ItemCarrito.objects.filter(usuario=request.user)
        serializer = ItemCarritoSerializer(items, many=True)
        total = sum(item.producto.precio_con_descuento * item.cantidad for item in items)
        return Response({
            "items": serializer.data,
            "total": total,
            "cantidad_items": items.count()
        })
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Agregar item al carrito"""
        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))
        talla = request.data.get('talla_seleccionada', '')
        color = request.data.get('color_seleccionado', '')
        
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return Response({"error": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        if producto.stock < cantidad:
            return Response({"error": "Stock insuficiente"}, status=status.HTTP_400_BAD_REQUEST)
        
        item, created = ItemCarrito.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            talla_seleccionada=talla,
            color_seleccionado=color,
            defaults={'cantidad': cantidad}
        )
        
        if not created:
            item.cantidad += cantidad
            item.save()
        
        serializer = ItemCarritoSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """Eliminar item del carrito"""
        item_id = request.data.get('item_id')
        try:
            item = ItemCarrito.objects.get(id=item_id, usuario=request.user)
            item.delete()
            return Response({"message": "Item eliminado"}, status=status.HTTP_204_NO_CONTENT)
        except ItemCarrito.DoesNotExist:
            return Response({"error": "Item no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Vaciar carrito"""
        ItemCarrito.objects.filter(usuario=request.user).delete()
        return Response({"message": "Carrito vaciado"}, status=status.HTTP_204_NO_CONTENT)

# ============ PEDIDO ============
class PedidoViewSet(viewsets.ModelViewSet):
    """ViewSet para pedidos"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'fecha_pedido']
    ordering_fields = ['fecha_pedido', 'total']
    ordering = ['-fecha_pedido']
    
    def get_queryset(self):
        """Retornar solo pedidos del usuario actual"""
        if self.request.user.is_staff:
            return Pedido.objects.all()
        return Pedido.objects.filter(usuario=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PedidoDetailSerializer
        return PedidoListSerializer
    
    def perform_create(self, serializer):
        """Crear pedido a partir del carrito"""
        import uuid
        numero_pedido = f"PED-{uuid.uuid4().hex[:8].upper()}"
        
        carrito_items = ItemCarrito.objects.filter(usuario=self.request.user)
        if not carrito_items.exists():
            raise ValueError("El carrito está vacío")
        
        total = sum(item.producto.precio_con_descuento * item.cantidad for item in carrito_items)
        
        pedido = serializer.save(
            usuario=self.request.user,
            numero_pedido=numero_pedido,
            total=total
        )
        
        # Crear items del pedido
        for carrito_item in carrito_items:
            ItemPedido.objects.create(
                pedido=pedido,
                producto=carrito_item.producto,
                cantidad=carrito_item.cantidad,
                precio_unitario=carrito_item.producto.precio_con_descuento,
                talla=carrito_item.talla_seleccionada,
                color=carrito_item.color_seleccionado
            )
        
        # Limpiar carrito
        carrito_items.delete()
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar pedido"""
        pedido = self.get_object()
        if pedido.estado in ['enviado', 'entregado', 'cancelado']:
            return Response({"error": "No se puede cancelar este pedido"}, status=status.HTTP_400_BAD_REQUEST)
        
        pedido.estado = 'cancelado'
        pedido.save()
        serializer = self.get_serializer(pedido)
        return Response(serializer.data)

# ============ RESENA ============
class ResenaViewSet(viewsets.ModelViewSet):
    """ViewSet para reseñas"""
    queryset = Resena.objects.all()
    serializer_class = ResenaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['producto', 'usuario', 'calificacion']
    ordering_fields = ['fecha_creacion', 'util_count', 'calificacion']
    ordering = ['-fecha_creacion']
    
    def perform_create(self, serializer):
        """Crear reseña"""
        serializer.save(usuario=self.request.user)
    
    @action(detail=True, methods=['post'])
    def marcar_util(self, request, pk=None):
        """Marcar reseña como útil"""
        resena = self.get_object()
        resena.util_count += 1
        resena.save()
        serializer = self.get_serializer(resena)
        return Response(serializer.data)
