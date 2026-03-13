"""
Módulo de autenticación para la aplicación.
Maneja registro, login, logout y verificación de usuarios.
"""
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from app.models import User, Session
from app.validators import EmailValidator


class AuthenticationError(Exception):
    """Excepción para errores de autenticación."""
    pass


class AuthService:
    """Servicio de autenticación para gestionar usuarios y sesiones."""
    
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.email_to_user_id: Dict[str, int] = {}
        self._next_user_id = 1
    
    def register(
        self,
        email: str,
        username: str,
        password: str,
        **profile_data
    ) -> Tuple[User, str]:
        """
        Registra un nuevo usuario.
        
        Args:
            email: Email del usuario.
            username: Nombre de usuario.
            password: Contraseña en texto plano.
            **profile_data: Datos adicionales del perfil.
            
        Returns:
            Tupla con (Usuario, token_de_sesión).
            
        Raises:
            AuthenticationError: Si el email ya está registrado o es inválido.
        """
        is_valid, error_msg = EmailValidator.validate(email)
        if not is_valid:
            raise AuthenticationError(f"Email inválido: {error_msg}")
        
        normalized_email = EmailValidator.normalize(email)
        if normalized_email in self.email_to_user_id:
            raise AuthenticationError("El email ya está registrado")
        
        if not username or len(username.strip()) < 3:
            raise AuthenticationError("El nombre de usuario debe tener al menos 3 caracteres")
        
        if len(password) < 8:
            raise AuthenticationError("La contraseña debe tener al menos 8 caracteres")
        
        password_hash, salt = User.hash_password(password)
        
        user = User(
            user_id=self._next_user_id,
            email=normalized_email,
            username=username.strip(),
            password_hash=password_hash
        )
        user.profile.update(profile_data)
        
        self.users[user.user_id] = user
        self.email_to_user_id[normalized_email] = user.user_id
        self._next_user_id += 1
        
        session = Session.create_session(user.user_id)
        self.sessions[session.session_id] = session
        
        return user, session.session_id
    
    def login(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[User, str]:
        """
        Inicia sesión de un usuario.
        
        Args:
            email: Email del usuario.
            password: Contraseña en texto plano.
            ip_address: Dirección IP del cliente.
            user_agent: User agent del navegador.
            
        Returns:
            Tupla con (Usuario, token_de_sesión).
            
        Raises:
            AuthenticationError: Si las credenciales son inválidas.
        """
        normalized_email = EmailValidator.normalize(email)
        if not normalized_email:
            raise AuthenticationError("Email inválido")
        
        user_id = self.email_to_user_id.get(normalized_email)
        if not user_id:
            raise AuthenticationError("Credenciales inválidas")
        
        user = self.users.get(user_id)
        if not user or not user.is_active:
            raise AuthenticationError("Credenciales inválidas")
        
        if not User.verify_password(password, user.password_hash, user.password_hash[:32]):
            raise AuthenticationError("Credenciales inválidas")
        
        session = Session.create_session(user.user_id)
        session.ip_address = ip_address
        session.user_agent = user_agent
        self.sessions[session.session_id] = session
        
        user.update_last_login()
        
        return user, session.session_id
    
    def logout(self, session_token: str) -> bool:
        """
        Cierra la sesión de un usuario.
        
        Args:
            session_token: Token de sesión a invalidar.
            
        Returns:
            True si se cerró la sesión, False si no existía.
        """
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False
    
    def get_current_user(self, session_token: str) -> Optional[User]:
        """
        Obtiene el usuario actual basado en el token de sesión.
        
        Args:
            session_token: Token de sesión.
            
        Returns:
            El usuario o None si la sesión es inválida.
        """
        session = self.sessions.get(session_token)
        if not session or not session.is_valid():
            return None
        
        user = self.users.get(session.user_id)
        if not user or not user.is_active:
            return None
        
        return user
    
    def verify_email(self, email: str) -> bool:
        """
        Verifica el email de un usuario.
        
        Args:
            email: Email a verificar.
            
        Returns:
            True si se verificó, False si no existe.
        """
        normalized_email = EmailValidator.normalize(email)
        user_id = self.email_to_user_id.get(normalized_email)
        if not user_id:
            return False
        
        user = self.users.get(user_id)
        if user:
            user.is_verified = True
            return True
        return False
    
    def change_password(
        self,
        email: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Cambia la contraseña de un usuario.
        
        Args:
            email: Email del usuario.
            old_password: Contraseña actual.
            new_password: Nueva contraseña.
            
        Returns:
            True si se cambió, False si falló.
        """
        normalized_email = EmailValidator.normalize(email)
        user_id = self.email_to_user_id.get(normalized_email)
        if not user_id:
            return False
        
        user = self.users.get(user_id)
        if not user:
            return False
        
        # El hash ya contiene la sal, no necesitamos extraerla
        if not User.verify_password(old_password, user.password_hash, ''):
            return False
        
        if len(new_password) < 8:
            return False
        
        password_hash, salt = User.hash_password(new_password)
        user.password_hash = password_hash
        
        return True
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por su email."""
        normalized_email = EmailValidator.normalize(email)
        user_id = self.email_to_user_id.get(normalized_email)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por su ID."""
        return self.users.get(user_id)
