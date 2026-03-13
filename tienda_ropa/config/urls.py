"""
URLs para la aplicación Tienda de Ropa.

Este módulo configura los routers de Django REST Framework para todos
los ViewSets y añade rutas adicionales para autenticación JWT.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.tienda.views import (
    CategoriaViewSet,
    ProductoViewSet,
    UsuarioViewSet,
    PedidoViewSet,
    CarritoViewSet,
    ResenaViewSet,
)

# Crear router y registrar ViewSets
router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'carrito', CarritoViewSet, basename='carrito')
router.register(r'resenas', ResenaViewSet, basename='resena')

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # API Routes
    path('api/', include(router.urls)),
    
    # Autenticación JWT
    path('api/auth/login/', TokenObtainPairView.as_view(), 
         name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), 
         name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), 
         name='token_verify'),
    
    # Health check endpoint
    path('api/health/', lambda request: {'status': 'ok'}, name='health_check'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Títulos del admin
admin.site.site_header = "Tienda de Ropa - Administración"
admin.site.site_title = "Tienda de Ropa Admin"
admin.site.index_title = "Panel de Control"
