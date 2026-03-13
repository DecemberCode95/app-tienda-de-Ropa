# Tienda de Ropa - Django REST Framework API

API REST profesional para una tienda de ropa construida con Django REST Framework, incluyendo autenticación JWT, gestión de productos, carritos, pedidos y reseñas.

## 📋 Características

- ✅ **Autenticación JWT** con tokens de acceso y refresh
- ✅ **Modelos completos**: Usuario, Producto, Categoría, Pedido, Carrito, Reseña
- ✅ **CRUD completo** para todos los modelos
- ✅ **Filtrado y búsqueda** avanzada de productos
- ✅ **Paginación** automática en listados
- ✅ **Validaciones** robustas en serializers
- ✅ **Permisos granulares** por acción
- ✅ **CORS habilitado** para frontends separados
- ✅ **Dockerizado** con PostgreSQL y Nginx
- ✅ **Documentación** completa de endpoints

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)

```bash
# Copiar archivo de entorno
cp .env.example .env

# Ajustar variables en .env si es necesario

# Levantar todos los servicios
docker-compose up --build

# La API estará disponible en http://localhost:8000
```

### Opción 2: Desarrollo Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Copiar archivo de entorno
cp .env.example .env

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Servidor de desarrollo
python manage.py runserver
```

## 📁 Estructura del Proyecto

```
tienda_ropa/
├── config/                 # Configuración de Django
│   ├── settings.py        # Configuración principal
│   ├── urls.py            # URLs principales
│   ├── wsgi.py            # WSGI config
│   └── asgi.py            # ASGI config
├── apps/
│   └── tienda/            # Aplicación principal
│       ├── models.py      # Modelos de datos
│       ├── serializers.py # Serializers DRF
│       ├── views.py       # ViewSets REST
│       └── apps.py        # AppConfig
├── tests/                 # Pruebas unitarias
├── docker-compose.yml     # Orquestación Docker
├── Dockerfile             # Imagen Docker
├── nginx.conf             # Configuración Nginx
├── requirements.txt       # Dependencias Python
└── manage.py              # CLI de Django
```

## 🔑 Endpoints de la API

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Obtener tokens JWT |
| POST | `/api/auth/refresh/` | Refresh token |
| POST | `/api/auth/verify/` | Verificar token |

### Categorías
| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/categorias/` | Listar categorías | Público |
| GET | `/api/categorias/{id}/` | Detalle categoría | Público |
| POST | `/api/categorias/` | Crear categoría | Admin |
| PUT | `/api/categorias/{id}/` | Actualizar categoría | Admin |
| DELETE | `/api/categorias/{id}/` | Eliminar categoría | Admin |
| GET | `/api/categorias/activas/` | Categorías activas | Público |
| GET | `/api/categorias/{id}/productos/` | Productos de categoría | Público |

### Productos
| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/productos/` | Listar productos | Público |
| GET | `/api/productos/{id}/` | Detalle producto | Público |
| POST | `/api/productos/` | Crear producto | Admin |
| PUT | `/api/productos/{id}/` | Actualizar producto | Admin |
| DELETE | `/api/productos/{id}/` | Eliminar producto | Admin |
| GET | `/api/productos/disponibles/` | Productos disponibles | Público |
| GET | `/api/productos/ofertas/` | Productos en oferta | Público |
| GET | `/api/productos/mas-vendidos/` | Más vendidos | Público |
| POST | `/api/productos/{id}/resenas/` | Añadir reseña | Auth |

**Parámetros de filtrado para productos:**
- `?categoria={id}` - Filtrar por categoría
- `?talla={XS,S,M,L,XL...}` - Filtrar por talla
- `?estado={disponible,agotado...}` - Filtrar por estado
- `?disponible=true` - Solo disponibles
- `?precio_min={valor}&precio_max={valor}` - Rango de precios
- `?search={texto}` - Búsqueda en nombre/descripción
- `?ordering={-precio,precio,nombre}` - Ordenamiento

### Usuarios
| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/usuarios/` | Listar usuarios | Admin |
| GET | `/api/usuarios/{id}/` | Detalle usuario | Propio/Admin |
| PUT | `/api/usuarios/{id}/` | Actualizar usuario | Propio/Admin |
| GET | `/api/usuarios/perfil/` | Mi perfil | Auth |
| PUT | `/api/usuarios/perfil/` | Actualizar mi perfil | Auth |
| GET | `/api/usuarios/mis-pedidos/` | Mis pedidos | Auth |
| GET | `/api/usuarios/estadisticas/` | Mis estadísticas | Auth |

### Pedidos
| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/pedidos/` | Listar pedidos | Admin |
| GET | `/api/pedidos/{id}/` | Detalle pedido | Propio/Admin |
| POST | `/api/pedidos/` | Crear pedido | Auth |
| GET | `/api/pedidos/mis-pedidos/` | Mis pedidos | Auth |
| POST | `/api/pedidos/{id}/cancelar/` | Cancelar pedido | Propio/Admin |
| POST | `/api/pedidos/{id}/enviar/` | Marcar enviado | Admin |
| POST | `/api/pedidos/{id}/entregar/` | Marcar entregado | Admin |

### Carrito
| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/carrito/` | Mi carrito | Auth |
| POST | `/api/carrito/agregar/` | Agregar producto | Auth |
| POST | `/api/carrito/actualizar/` | Actualizar cantidad | Auth |
| DELETE | `/api/carrito/eliminar/` | Eliminar producto | Auth |
| DELETE | `/api/carrito/vaciar/` | Vaciar carrito | Auth |

### Reseñas
| Método | Endpoint | Descripción | Permiso |
|--------|----------|-------------|---------|
| GET | `/api/resenas/` | Listar reseñas | Público |
| GET | `/api/resenas/{id}/` | Detalle reseña | Público |
| POST | `/api/resenas/` | Crear reseña | Auth |
| PUT | `/api/resenas/{id}/` | Actualizar reseña | Autor |
| DELETE | `/api/resenas/{id}/` | Eliminar reseña | Autor/Admin |
| GET | `/api/resenas/producto/{id}/` | Reseñas de producto | Público |
| POST | `/api/resenas/{id}/votar/` | Votar reseña | Auth |

## 🔧 Variables de Entorno

Copiar `.env.example` a `.env` y configurar:

```bash
# Django
DEBUG=True
SECRET_KEY=tu-clave-secreta-muy-segura
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DB_NAME=tienda_ropa_db
DB_USER=tienda_user
DB_PASSWORD=tu-password
DB_HOST=db
DB_PORT=5432

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## 🧪 Pruebas

```bash
# Ejecutar pruebas
python manage.py test

# Con coverage
coverage run manage.py test
coverage report
```

## 📊 Modelos de Datos

### Usuario (AbstractUser)
- email (único)
- telefono, fecha_nacimiento
- tipo_usuario (cliente, vip, admin)
- direccion, ciudad, codigo_postal, pais
- newsletter

### Categoria
- nombre, descripcion, imagen
- activa, fecha_creacion

### Producto
- nombre, descripcion, precio
- talla (XS, S, M, L, XL, XXL, XXXL)
- stock, categoria (FK)
- imagen, imagenes_adicionales
- estado (disponible, agotado, proximamente, descatalogado)

### Pedido
- usuario (FK), productos (JSON)
- subtotal, impuestos, gastos_envio, total
- estado (pendiente, confirmado, preparando, enviado, entregado, cancelado)
- metodo_pago, direccion_envio
- numero_seguimiento, fechas

### Carrito
- usuario (OneToOne), productos (JSON)
- fecha_creacion, fecha_actualizacion

### Reseña
- usuario (FK), producto (FK)
- calificacion (1-5), comentario, titulo
- verificada, util, no_util

## 🛡️ Seguridad

- Contraseñas hasheadas con PBKDF2
- Tokens JWT con expiración configurable
- Validación de entrada en todos los endpoints
- Rate limiting con Nginx
- Headers de seguridad HTTP
- CORS configurado

## 📦 Producción

Para desplegar en producción:

```bash
# Construir imágenes
docker-compose -f docker-compose.yml build

# Levantar con Nginx
docker-compose --profile production up -d

# Ver logs
docker-compose logs -f
```

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push (`git push origin feature/nueva-funcionalidad`)
5. Pull Request

## 📄 Licencia

MIT License

## 📞 Soporte

Para issues o preguntas, abrir un issue en GitHub.

---

**Hecho con ❤️ usando Django REST Framework**
