"""
Aplicación principal con rutas API para productos y autenticación.
Usa Flask como framework web.
"""
from flask import Flask, request, jsonify, g
from functools import wraps
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models import User, Product, Session
from app.auth import AuthService, AuthenticationError
from app.validators import EmailValidator


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Servicio de autenticación global
auth_service = AuthService()

# Catálogo de productos en memoria (simulación de base de datos)
products_db: Dict[int, Product] = {}
_next_product_id = 1

# Datos de ejemplo
def seed_data():
    """Carga datos de ejemplo en la aplicación."""
    global _next_product_id
    
    # Usuario de ejemplo
    try:
        user, _ = auth_service.register(
            email="demo@example.com",
            username="demouser",
            password="password123",
            bio="Usuario de demostración"
        )
    except AuthenticationError:
        pass
    
    # Productos de ejemplo
    sample_products = [
        Product(1, "Laptop Pro", "Laptop de alto rendimiento", 999.99, 50, "electronics"),
        Product(2, "Mouse Inalámbrico", "Mouse ergonómico inalámbrico", 29.99, 200, "electronics"),
        Product(3, "Teclado Mecánico", "Teclado mecánico RGB", 79.99, 150, "electronics"),
        Product(4, "Monitor 4K", "Monitor 27 pulgadas 4K", 399.99, 30, "electronics"),
        Product(5, "Silla Ergonómica", "Silla de oficina ergonómica", 249.99, 75, "furniture"),
    ]
    
    for product in sample_products:
        products_db[product.product_id] = product
    
    _next_product_id = 6


def require_auth(f):
    """Decorador para requerir autenticación en las rutas."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = request.headers.get('X-Session-Token')
        if not session_token:
            return jsonify({'error': 'Token de sesión requerido'}), 401
        
        current_user = auth_service.get_current_user(session_token)
        if not current_user:
            return jsonify({'error': 'Sesión inválida o expirada'}), 401
        
        g.current_user = current_user
        g.session_token = session_token
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """Decorador para requerir rol de administrador."""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if g.current_user.role != 'admin':
            return jsonify({'error': 'Se requieren privilegios de administrador'}), 403
        return f(*args, **kwargs)
    
    return decorated_function


# ==================== RUTAS DE AUTENTICACIÓN ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registra un nuevo usuario."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    required_fields = ['email', 'username', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    try:
        user, session_token = auth_service.register(
            email=data['email'],
            username=data['username'],
            password=data['password'],
            **{k: v for k, v in data.items() if k not in required_fields}
        )
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': user.to_dict(),
            'session_token': session_token
        }), 201
    
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Inicia sesión de un usuario."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email y contraseña requeridos'}), 400
    
    try:
        user, session_token = auth_service.login(
            email=data['email'],
            password=data['password'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Login exitoso',
            'user': user.to_dict(),
            'session_token': session_token
        })
    
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401


@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Cierra la sesión del usuario actual."""
    auth_service.logout(g.session_token)
    return jsonify({'message': 'Sesión cerrada exitosamente'})


@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Obtiene información del usuario actual."""
    return jsonify({'user': g.current_user.to_dict()})


@app.route('/api/auth/change-password', methods=['POST'])
@require_auth
def change_password():
    """Cambia la contraseña del usuario actual."""
    data = request.get_json()
    
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Contraseñas requeridas'}), 400
    
    success = auth_service.change_password(
        email=g.current_user.email,
        old_password=data['old_password'],
        new_password=data['new_password']
    )
    
    if success:
        return jsonify({'message': 'Contraseña cambiada exitosamente'})
    else:
        return jsonify({'error': 'Contraseña actual incorrecta o nueva contraseña inválida'}), 400


# ==================== RUTAS DE PRODUCTOS ====================

@app.route('/api/productos', methods=['GET'])
def get_products():
    """
    Obtiene lista de productos con filtrado y paginación.
    Query params: category, min_price, max_price, search, page, per_page
    """
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search = request.args.get('search', '').lower()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    filtered_products: List[Product] = []
    
    for product in products_db.values():
        if category and product.category != category.lower():
            continue
        if min_price is not None and product.price < min_price:
            continue
        if max_price is not None and product.price > max_price:
            continue
        if search and search not in product.name.lower() and search not in product.description.lower():
            continue
        if not product.is_available:
            continue
        
        filtered_products.append(product)
    
    # Paginación
    total = len(filtered_products)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_products = filtered_products[start:end]
    
    return jsonify({
        'products': [p.to_dict() for p in paginated_products],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    })


@app.route('/api/productos/<int:product_id>', methods=['GET'])
def get_product(product_id: int):
    """Obtiene un producto por su ID."""
    product = products_db.get(product_id)
    
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    return jsonify({'product': product.to_dict()})


@app.route('/api/productos', methods=['POST'])
@require_auth
@admin_required
def create_product():
    """Crea un nuevo producto (solo administradores)."""
    global _next_product_id
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    required_fields = ['name', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    product = Product(
        product_id=_next_product_id,
        name=data['name'],
        description=data.get('description', ''),
        price=float(data['price']),
        stock=int(data.get('stock', 0)),
        category=data.get('category', 'general'),
        tags=data.get('tags', [])
    )
    
    products_db[product.product_id] = product
    _next_product_id += 1
    
    return jsonify({
        'message': 'Producto creado exitosamente',
        'product': product.to_dict()
    }), 201


@app.route('/api/productos/<int:product_id>', methods=['PUT'])
@require_auth
@admin_required
def update_product(product_id: int):
    """Actualiza un producto existente (solo administradores)."""
    product = products_db.get(product_id)
    
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    if 'name' in data:
        product.name = data['name'].strip()
    if 'description' in data:
        product.description = data['description'].strip()
    if 'price' in data:
        product.price = max(0.0, float(data['price']))
    if 'stock' in data:
        product.stock = max(0, int(data['stock']))
        product.is_available = product.stock > 0
    if 'category' in data:
        product.category = data['category'].lower().strip()
    if 'tags' in data:
        product.tags = data['tags']
    
    return jsonify({
        'message': 'Producto actualizado exitosamente',
        'product': product.to_dict()
    })


@app.route('/api/productos/<int:product_id>', methods=['DELETE'])
@require_auth
@admin_required
def delete_product(product_id: int):
    """Elimina un producto (solo administradores)."""
    if product_id not in products_db:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    del products_db[product_id]
    
    return jsonify({'message': 'Producto eliminado exitosamente'})


# ==================== RUTAS DE UTILIDAD ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica el estado de la aplicación."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/validate-email', methods=['POST'])
def validate_email():
    """Valida una dirección de email."""
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({'error': 'Email requerido'}), 400
    
    is_valid, error_msg = EmailValidator.validate(data['email'])
    
    return jsonify({
        'email': data['email'],
        'is_valid': is_valid,
        'error': error_msg,
        'is_common_domain': EmailValidator.is_common_domain(data['email']) if is_valid else False
    })


# Inicializar datos de ejemplo
seed_data()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
