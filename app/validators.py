"""
Validador de emails con expresiones regulares y verificación de dominios.
"""
import re
from typing import Tuple, Optional


class EmailValidator:
    """Clase para validar direcciones de email."""
    
    # Patrón regex para validación básica de email
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # Dominios comunes para verificación adicional
    COMMON_DOMAINS = {
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'icloud.com', 'protonmail.com', 'aol.com', 'mail.com'
    }
    
    @classmethod
    def validate(cls, email: str) -> Tuple[bool, Optional[str]]:
        """
        Valida una dirección de email.
        
        Args:
            email: La dirección de email a validar.
            
        Returns:
            Tupla con (es_valido, mensaje_de_error).
            Si es válido, mensaje_de_error es None.
        """
        if not email or not isinstance(email, str):
            return False, "El email no puede estar vacío"
        
        email = email.strip().lower()
        
        if len(email) > 254:
            return False, "El email es demasiado largo (máximo 254 caracteres)"
        
        if not cls.EMAIL_PATTERN.match(email):
            return False, "Formato de email inválido"
        
        local_part, domain = email.rsplit('@', 1)
        
        if len(local_part) > 64:
            return False, "La parte local del email es demasiado larga"
        
        if domain.startswith('.') or domain.endswith('.'):
            return False, "El dominio no puede empezar o terminar con un punto"
        
        if '..' in email:
            return False, "El email no puede tener puntos consecutivos"
        
        if local_part.startswith('.') or local_part.endswith('.'):
            return False, "La parte local no puede empezar o terminar con un punto"
        
        return True, None
    
    @classmethod
    def is_common_domain(cls, email: str) -> bool:
        """Verifica si el email usa un dominio común."""
        if '@' not in email:
            return False
        domain = email.split('@')[1].lower()
        return domain in cls.COMMON_DOMAINS
    
    @classmethod
    def normalize(cls, email: str) -> Optional[str]:
        """
        Normaliza una dirección de email (minúsculas, sin espacios).
        
        Args:
            email: La dirección de email a normalizar.
            
        Returns:
            El email normalizado o None si es inválido.
        """
        is_valid, _ = cls.validate(email)
        if not is_valid:
            return None
        return email.strip().lower()
