# 🛍️ Tienda de Ropa - E-commerce Django REST

Aplicación completa de e-commerce para venta de ropa desarrollada con Django REST Framework, React (frontend) y PostgreSQL.

## 📋 Características Principales

### Backend (Django REST)
- ✅ **API RESTful** completa con autenticación JWT
- ✅ **Gestión de Usuarios** con perfiles personalizados
- ✅ **Catálogo de Productos** con categorías, búsqueda y filtros
- ✅ **Carrito de Compras** persistente
- ✅ **Sistema de Pedidos** completo
- ✅ **Reseñas y Calificaciones** de productos
- ✅ **Descuentos y Promociones**
- ✅ **Gestión de Stock** en tiempo real
- ✅ **Admin Dashboard** de Django
- ✅ **Documentación API** con drf-spectacular

## 🛠️ Stack Tecnológico

### Backend
- **Framework**: Django 4.2
- **API**: Django REST Framework
- **Autenticación**: JWT (Simple JWT)
- **Base de Datos**: PostgreSQL
- **Cache**: Redis
- **Almacenamiento**: AWS S3
- **Documentación**: drf-spectacular (OpenAPI 3.0)
- **Testing**: pytest, pytest-django

### DevOps
- **Containerización**: Docker
- **Orquestación**: Docker Compose
- **Servidor**: Gunicorn + Nginx

## 📁 Estructura del Proyecto

```
app-tienda-de-Ropa/
├── config/              # Configuración del proyecto
│   ├── settings.py     # Configuración de Django
│   ├── urls.py         # URLs principales
│   ├── wsgi.py         # WSGI application
│   └── __init__.py
├── shop/               # Aplicación principal
│   ├── models.py       # Modelos de base de datos
│   ├── serializers.py  # Serializadores DRF
│   ├── views.py        # ViewSets y vistas
│   ├── urls.py         # URLs de la app
│   ├── admin.py        # Admin configuration
│   ├── filters.py      # Filtros personalizados
│   └── tests.py        # Tests unitarios
├── manage.py           # Script de gestión de Django
├── requirements.txt    # Dependencias Python
├── .env.example        # Variables de entorno (ejemplo)
├── Dockerfile          # Configuración Docker
├── docker-compose.yml  # Orquestación con Docker
└── README.md          # Este archivo
```

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Docker y Docker Compose (opcional)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/DecemberCode95/app-tienda-de-Ropa.git
cd app-tienda-de-Ropa
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Migraciones de Base de Datos

```bash
python manage.py migrate
```

### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 7. Recopilar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 8. Ejecutar Servidor de Desarrollo

```bash
python manage.py runserver
```

## 🐳 Ejecutar con Docker

```bash
docker-compose up -d
```

Esto creará:
- Contenedor de Django
- Contenedor de PostgreSQL
- Contenedor de Redis

## 📚 Documentación de API

La documentación de la API está disponible en:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

## 🔐 Autenticación

### Obtener Token JWT

```bash
POST /api/auth/login/
{
    "username": "usuario",
    "password": "contraseña"
}
```

Respuesta:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Usar Token en Requests

```bash
Authorization: Bearer <access_token>
```

## 🧪 Testing

Ejecutar tests:

```bash
pytest
```

Con cobertura:

```bash
pytest --cov=shop --cov-report=html
```

## 📊 Modelos Principales

### Usuario
- Heredado de AbstractUser
- Campos adicionales: teléfono, dirección, documento de identidad, etc.

### Producto
- Nombre, descripción, precio
- Categoría, stock, talla y colores disponibles
- Imágenes múltiples
- Descuentos y calificación promedio

### Pedido
- Usuario, número único de pedido
- Items con cantidad y precio
- Estados: pendiente, confirmado, enviado, entregado, cancelado
- Cálculo automático de impuestos y envío

### Carrito
- Items del carrito con producto, cantidad, talla y color
- Persistencia por usuario
- Sincronización multi-dispositivo

### Reseña
- Usuario, producto, calificación (1-5)
- Comentario, fotos
- Marque como útil
- Verificación de compra

## 🔄 Flujo de una Compra

1. Usuario se registra/inicia sesión
2. Explora productos (listado, búsqueda, filtros)
3. Lee reseñas de otros usuarios
4. Agrega productos al carrito
5. Revisa el carrito
6. Procede al checkout
7. Realiza el pago
8. Se crea un pedido
9. Recibe confirmación por email
10. El vendedor prepara el pedido
11. Se marca como enviado
12. Usuario recibe el producto
13. Usuario puede dejar una reseña

## 🚀 Endpoints Principales

### Autenticación
- `POST /api/auth/register/` - Registro
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refrescar token
- `POST /api/auth/logout/` - Logout

### Productos
- `GET /api/productos/` - Listar productos
- `POST /api/productos/` - Crear producto (admin)
- `GET /api/productos/{id}/` - Detalle producto
- `PUT /api/productos/{id}/` - Actualizar
- `DELETE /api/productos/{id}/` - Eliminar

### Carrito
- `GET /api/carrito/` - Ver carrito
- `POST /api/carrito/items/` - Agregar item
- `PUT /api/carrito/items/{id}/` - Actualizar cantidad
- `DELETE /api/carrito/items/{id}/` - Eliminar item

### Pedidos
- `GET /api/pedidos/` - Mis pedidos
- `POST /api/pedidos/` - Crear pedido
- `GET /api/pedidos/{id}/` - Detalle pedido
- `PUT /api/pedidos/{id}/` - Actualizar estado

### Reseñas
- `GET /api/resenas/` - Listar reseñas
- `POST /api/productos/{id}/resenas/` - Crear reseña
- `PUT /api/resenas/{id}/` - Actualizar reseña

## 🔮 Próximas Mejoras

- [ ] Integración con Stripe/PayPal
- [ ] Sistema de notificaciones por WebSocket
- [ ] Análisis de vendedores en tiempo real
- [ ] Recomendaciones con ML
- [ ] Chat en vivo con soporte
- [ ] App móvil nativa
- [ ] Analytics completo
- [ ] Marketplace multi-vendedor avanzado

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE`.

## 📧 Contacto

- **Desarrollador**: Daniel Roa
- **Email**: [tu-email@ejemplo.com](mailto:tu-email@ejemplo.com)
- **GitHub**: [@DecemberCode95](https://github.com/DecemberCode95)
- **LinkedIn**: [linkedin.com/in/tu-perfil](https://linkedin.com)

## 🙏 Agradecimientos

Gracias a:
- Django Community
- DRF Community
- Qwen AI por la asistencia en desarrollo

---

**Última actualización**: Marzo 2026
**Estado del Proyecto**: 🚀 En Desarrollo Activo
