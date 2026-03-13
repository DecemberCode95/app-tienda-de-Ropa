from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet, CategoriaViewSet, ProductoViewSet,
    CarritoViewSet, PedidoViewSet, ResenaViewSet
)

# Crear router para registrar los ViewSets
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'carrito', CarritoViewSet, basename='carrito')
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'resenas', ResenaViewSet, basename='resena')

# URLs de la aplicación
urlpatterns = [
    path('', include(router.urls)),
]
