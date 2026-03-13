"""
Módulo de modelos para la aplicación.
Incluye modelos de usuario, productos y sesiones.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import hashlib
import secrets


class User:
    """Modelo de usuario para autenticación."""
    
    def __init__(
        self,
        user_id: int,
        email: str,
        username: str,
        password_hash: str,
        created_at: Optional[datetime] = None,
        is_active: bool = True,
        is_verified: bool = False,
        role: str = 'user'
    ):
        self.user_id = user_id
        self.email = email.lower().strip()
        self.username = username.strip()
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
        self.is_active = is_active
        self.is_verified = is_verified
        self.role = role
        self.last_login: Optional[datetime] = None
        self.profile: Dict[str, Any] = {}
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convierte el usuario a diccionario."""
        data = {
            'user_id': self.user_id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'role': self.role,
            'profile': self.profile
        }
        if include_sensitive:
            data['password_hash'] = self.password_hash
            data['last_login'] = self.last_login.isoformat() if self.last_login else None
        return data
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple:
        """Hashea una contraseña con sal."""
        if salt is None:
            salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        # Retornar hash completo con sal prefixada para almacenamiento
        return salt + password_hash, salt
    
    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str) -> bool:
        """Verifica si una contraseña coincide con el hash almacenado."""
        # El hash almacenado ya incluye la sal en los primeros 32 caracteres
        if len(stored_hash) >= 96:  # 32 (sal) + 64 (hash)
            salt = stored_hash[:32]
        
        new_hash, _ = User.hash_password(password, salt)
        return secrets.compare_digest(new_hash, stored_hash)
    
    def update_last_login(self):
        """Actualiza la fecha del último inicio de sesión."""
        self.last_login = datetime.utcnow()


class Product:
    """Modelo de producto para el catálogo."""
    
    def __init__(
        self,
        product_id: int,
        name: str,
        description: str,
        price: float,
        stock: int = 0,
        category: str = 'general',
        created_at: Optional[datetime] = None,
        is_available: bool = True
    ):
        self.product_id = product_id
        self.name = name.strip()
        self.description = description.strip()
        self.price = max(0.0, price)
        self.stock = max(0, stock)
        self.category = category.lower().strip()
        self.created_at = created_at or datetime.utcnow()
        self.is_available = is_available and stock > 0
        self.images: List[str] = []
        self.tags: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el producto a diccionario."""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
            'is_available': self.is_available,
            'images': self.images,
            'tags': self.tags
        }
    
    def add_stock(self, quantity: int):
        """Añade stock al producto."""
        if quantity > 0:
            self.stock += quantity
            self.is_available = True
    
    def remove_stock(self, quantity: int) -> bool:
        """Remueve stock del producto."""
        if quantity > 0 and self.stock >= quantity:
            self.stock -= quantity
            self.is_available = self.stock > 0
            return True
        return False


class Session:
    """Modelo de sesión para autenticación."""
    
    def __init__(
        self,
        session_id: str,
        user_id: int,
        expires_at: datetime,
        created_at: Optional[datetime] = None
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.expires_at = expires_at
        self.created_at = created_at or datetime.utcnow()
        self.ip_address: Optional[str] = None
        self.user_agent: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Verifica si la sesión es válida."""
        return datetime.utcnow() < self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la sesión a diccionario."""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
    
    @staticmethod
    def generate_session_id() -> str:
        """Genera un ID de sesión único."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_session(user_id: int, duration_hours: int = 24) -> 'Session':
        """Crea una nueva sesión para un usuario."""
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        return Session(
            session_id=Session.generate_session_id(),
            user_id=user_id,
            expires_at=expires_at
        )
