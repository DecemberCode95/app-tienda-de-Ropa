# Proyecto API REST - E-Commerce

## Descripción

Proyecto de ejemplo que implementa una API REST completa para un sistema de e-commerce con autenticación de usuarios, gestión de productos y validación de emails.

## Estructura del Proyecto

```
/workspace
├── app/                      # Módulo principal de la aplicación
│   ├── __init__.py
│   ├── models.py            # Modelos de datos (User, Product, Session)
│   ├── auth.py              # Servicio de autenticación
│   └── validators.py        # Validadores (EmailValidator)
├── tests/                    # Pruebas unitarias
│   └── test_auth.py         # Pruebas del módulo de autenticación
├── docs/                     # Documentación
├── static/                   # Archivos estáticos
├── templates/                # Plantillas HTML
├── app.py                    # Aplicación Flask principal
└── README.md                 # Este archivo
```

## Características

### 🔐 Autenticación
- Registro de usuarios con validación de email
- Login/Logout con tokens de sesión
- Cambio de contraseña seguro
- Verificación de emails
- Hash de contraseñas con PBKDF2-SHA256

### 📦 Gestión de Productos
- CRUD completo de productos
- Filtrado por categoría, precio y búsqueda
- Paginación de resultados
- Control de stock
- Solo administradores pueden crear/editar/eliminar

### ✉️ Validación de Emails
- Validación con expresiones regulares
- Verificación de longitud máxima
- Detección de puntos consecutivos
- Identificación de dominios comunes

## Instalación

```bash
# Instalar dependencias
pip install flask

# Ejecutar la aplicación
python app.py
```

## API Endpoints

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/register` | Registrar nuevo usuario |
| POST | `/api/auth/login` | Iniciar sesión |
| POST | `/api/auth/logout` | Cerrar sesión |
| GET | `/api/auth/me` | Obtener usuario actual |
| POST | `/api/auth/change-password` | Cambiar contraseña |

### Productos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/productos` | Listar productos (con filtros) |
| GET | `/api/productos/<id>` | Obt producto por ID |
| POST | `/api/productos` | Crear producto (admin) |
| PUT | `/api/productos/<id>` | Actualizar producto (admin) |
| DELETE | `/api/productos/<id>` | Eliminar producto (admin) |

### Utilidad

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/health` | Verificar estado |
| POST | `/api/validate-email` | Validar email |

## Ejemplos de Uso

### Registrar Usuario

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "username": "nuevousuario",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "password123"
  }'
```

### Obtener Productos con Filtros

```bash
curl "http://localhost:5000/api/productos?category=electronics&min_price=50&max_price=500&page=1&per_page=10"
```

### Crear Producto (requiere admin)

```bash
curl -X POST http://localhost:5000/api/productos \
  -H "Content-Type: application/json" \
  -H "X-Session-Token: TU_TOKEN_AQUI" \
  -d '{
    "name": "Nuevo Producto",
    "description": "Descripción del producto",
    "price": 99.99,
    "stock": 50,
    "category": "electronics"
  }'
```

## Ejecutar Pruebas

```bash
python -m unittest tests.test_auth -v
```

## Ideas para Nuevas Rutas y Funcionalidades

### 🚀 Rutas Sugeridas

1. **`/api/recomendaciones`** - Sistema de recomendación basado en IA
   - Productos similares
   - Basado en historial de navegación
   - Machine learning para personalización

2. **`/api/carrito`** - Gestión de carrito de compras
   - Añadir/eliminar productos
   - Actualizar cantidades
   - Calcular totales con impuestos

3. **`/api/ordenes`** - Gestión de órdenes
   - Crear orden desde carrito
   - Historial de órdenes
   - Seguimiento de envíos

4. **`/api/resenas`** - Sistema de reseñas y calificaciones
   - Calificar productos
   - Comentarios verificados
   - Moderación de contenido

5. **`/api/notificaciones`** - Sistema de notificaciones
   - WebSockets para tiempo real
   - Email marketing
   - Alertas de stock

6. **`/api/analytics`** - Dashboard analítico
   - Ventas por período
   - Productos más vendidos
   - Métricas de usuarios

7. **`/api/cupones`** - Sistema de descuentos
   - Códigos promocionales
   - Descuentos por volumen
   - Ofertas temporales

8. **`/api/wishlist`** - Lista de deseos
   - Guardar productos favoritos
   - Alertas de precio
   - Compartir listas

### 💡 Mejoras de Rendimiento Sugeridas

1. **Cacheo de consultas** - Redis para productos frecuentes
2. **Indexación de base de datos** - Índices en campos de búsqueda
3. **Lazy loading** - Carga diferida de imágenes
4. **Connection pooling** - Pool de conexiones a BD
5. **Query optimization** - SELECT específico, evitar N+1
6. **CDN para estáticos** - Servir assets desde CDN
7. **Compresión Gzip** - Reducir tamaño de respuestas
8. **Rate limiting** - Prevenir abuso de API

### 🔒 Mejoras de Seguridad

1. **2FA** - Autenticación de dos factores
2. **OAuth2** - Login con Google/Facebook
3. **JWT** - Tokens JWT en lugar de sesiones
4. **HTTPS** - Forzar conexiones seguras
5. **CORS** - Configurar políticas CORS estrictas
6. **Input sanitization** - Limpiar todas las entradas
7. **SQL injection prevention** - Usar ORM o queries parametrizadas

## Licencia

MIT License
