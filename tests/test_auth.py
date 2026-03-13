"""
Pruebas unitarias para el módulo de autenticación.
Usa unittest como framework de testing.
"""
import unittest
from datetime import datetime, timedelta
from app.models import User, Session, Product
from app.auth import AuthService, AuthenticationError
from app.validators import EmailValidator


class TestEmailValidator(unittest.TestCase):
    """Pruebas para el validador de emails."""
    
    def test_valid_emails(self):
        """Prueba emails válidos."""
        valid_emails = [
            'user@example.com',
            'user.name@example.com',
            'user+tag@example.com',
            'user123@test.org',
            'USER@EXAMPLE.COM'
        ]
        
        for email in valid_emails:
            is_valid, error = EmailValidator.validate(email)
            self.assertTrue(is_valid, f"Email {email} debería ser válido")
    
    def test_invalid_emails(self):
        """Prueba emails inválidos."""
        invalid_emails = [
            '',
            'invalid',
            '@example.com',
            'user@',
            'user@.com',
            'user@example.',
            'user..name@example.com',
            '.user@example.com',
            'user.@example.com',
            'a' * 255 + '@example.com'  # Demasiado largo
        ]
        
        for email in invalid_emails:
            is_valid, error = EmailValidator.validate(email)
            self.assertFalse(is_valid, f"Email {email} debería ser inválido")
    
    def test_normalize_email(self):
        """Prueba normalización de emails."""
        self.assertEqual(
            EmailValidator.normalize('  USER@Example.COM  '),
            'user@example.com'
        )
        self.assertIsNone(EmailValidator.normalize('invalid'))
    
    def test_common_domain(self):
        """Prueba detección de dominios comunes."""
        self.assertTrue(EmailValidator.is_common_domain('user@gmail.com'))
        self.assertTrue(EmailValidator.is_common_domain('user@yahoo.com'))
        self.assertFalse(EmailValidator.is_common_domain('user@customdomain.com'))


class TestUserModel(unittest.TestCase):
    """Pruebas para el modelo de usuario."""
    
    def test_user_creation(self):
        """Prueba creación de usuario."""
        password_hash, salt = User.hash_password('password123')
        user = User(
            user_id=1,
            email='test@example.com',
            username='testuser',
            password_hash=password_hash
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_verified)
    
    def test_password_hashing(self):
        """Prueba hasheo de contraseñas."""
        password = 'securepassword123'
        password_hash, salt = User.hash_password(password)
        
        self.assertNotEqual(password, password_hash)
        self.assertTrue(User.verify_password(password, password_hash, salt))
        self.assertFalse(User.verify_password('wrongpassword', password_hash, salt))
    
    def test_user_to_dict(self):
        """Prueba conversión a diccionario."""
        password_hash, salt = User.hash_password('password123')
        user = User(
            user_id=1,
            email='test@example.com',
            username='testuser',
            password_hash=password_hash
        )
        
        user_dict = user.to_dict()
        self.assertIn('user_id', user_dict)
        self.assertIn('email', user_dict)
        self.assertNotIn('password_hash', user_dict)
        
        sensitive_dict = user.to_dict(include_sensitive=True)
        self.assertIn('password_hash', sensitive_dict)


class TestSessionModel(unittest.TestCase):
    """Pruebas para el modelo de sesión."""
    
    def test_session_creation(self):
        """Prueba creación de sesión."""
        session = Session.create_session(user_id=1, duration_hours=24)
        
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.user_id, 1)
        self.assertTrue(session.is_valid())
    
    def test_session_expiration(self):
        """Prueba expiración de sesión."""
        past_time = datetime.utcnow() - timedelta(hours=2)
        session = Session(
            session_id='test123',
            user_id=1,
            expires_at=past_time
        )
        
        self.assertFalse(session.is_valid())
    
    def test_session_id_uniqueness(self):
        """Prueba unicidad de IDs de sesión."""
        ids = set()
        for _ in range(100):
            session_id = Session.generate_session_id()
            self.assertNotIn(session_id, ids)
            ids.add(session_id)


class TestAuthService(unittest.TestCase):
    """Pruebas para el servicio de autenticación."""
    
    def setUp(self):
        """Configura un servicio de autenticación limpio para cada prueba."""
        self.auth_service = AuthService()
    
    def test_register_user(self):
        """Prueba registro de usuario."""
        user, session_token = self.auth_service.register(
            email='newuser@example.com',
            username='newuser',
            password='password123'
        )
        
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.username, 'newuser')
        self.assertIsNotNone(session_token)
    
    def test_register_duplicate_email(self):
        """Prueba registro con email duplicado."""
        self.auth_service.register(
            email='duplicate@example.com',
            username='user1',
            password='password123'
        )
        
        with self.assertRaises(AuthenticationError):
            self.auth_service.register(
                email='duplicate@example.com',
                username='user2',
                password='password456'
            )
    
    def test_register_invalid_email(self):
        """Prueba registro con email inválido."""
        with self.assertRaises(AuthenticationError):
            self.auth_service.register(
                email='invalid-email',
                username='user',
                password='password123'
            )
    
    def test_register_weak_password(self):
        """Prueba registro con contraseña débil."""
        with self.assertRaises(AuthenticationError):
            self.auth_service.register(
                email='user@example.com',
                username='user',
                password='short'
            )
    
    def test_login_success(self):
        """Prueba login exitoso."""
        self.auth_service.register(
            email='login@example.com',
            username='loginuser',
            password='password123'
        )
        
        user, session_token = self.auth_service.login(
            email='login@example.com',
            password='password123'
        )
        
        self.assertEqual(user.email, 'login@example.com')
        self.assertIsNotNone(session_token)
    
    def test_login_wrong_password(self):
        """Prueba login con contraseña incorrecta."""
        self.auth_service.register(
            email='wrongpass@example.com',
            username='user',
            password='correctpassword'
        )
        
        with self.assertRaises(AuthenticationError):
            self.auth_service.login(
                email='wrongpass@example.com',
                password='wrongpassword'
            )
    
    def test_login_nonexistent_user(self):
        """Prueba login con usuario inexistente."""
        with self.assertRaises(AuthenticationError):
            self.auth_service.login(
                email='nonexistent@example.com',
                password='password123'
            )
    
    def test_logout(self):
        """Prueba logout."""
        user, session_token = self.auth_service.register(
            email='logout@example.com',
            username='logoutuser',
            password='password123'
        )
        
        self.assertTrue(self.auth_service.get_current_user(session_token) is not None)
        
        result = self.auth_service.logout(session_token)
        self.assertTrue(result)
        self.assertIsNone(self.auth_service.get_current_user(session_token))
    
    def test_get_current_user_invalid_session(self):
        """Prueba obtener usuario con sesión inválida."""
        user = self.auth_service.get_current_user('invalid-token')
        self.assertIsNone(user)
    
    def test_change_password(self):
        """Prueba cambio de contraseña."""
        self.auth_service.register(
            email='changepass@example.com',
            username='changeuser',
            password='oldpassword123'
        )
        
        result = self.auth_service.change_password(
            email='changepass@example.com',
            old_password='oldpassword123',
            new_password='newpassword456'
        )
        
        self.assertTrue(result)
        
        # Verificar que la nueva contraseña funciona
        user, _ = self.auth_service.login(
            email='changepass@example.com',
            password='newpassword456'
        )
        self.assertIsNotNone(user)
        
        # Verificar que la antigua ya no funciona
        with self.assertRaises(AuthenticationError):
            self.auth_service.login(
                email='changepass@example.com',
                password='oldpassword123'
            )
    
    def test_verify_email(self):
        """Prueba verificación de email."""
        self.auth_service.register(
            email='verify@example.com',
            username='verifyuser',
            password='password123'
        )
        
        user = self.auth_service.get_user_by_email('verify@example.com')
        self.assertFalse(user.is_verified)
        
        result = self.auth_service.verify_email('verify@example.com')
        self.assertTrue(result)
        
        user = self.auth_service.get_user_by_email('verify@example.com')
        self.assertTrue(user.is_verified)


class TestProductModel(unittest.TestCase):
    """Pruebas para el modelo de producto."""
    
    def test_product_creation(self):
        """Prueba creación de producto."""
        product = Product(
            product_id=1,
            name='Test Product',
            description='A test product',
            price=99.99,
            stock=10,
            category='test'
        )
        
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, 99.99)
        self.assertEqual(product.stock, 10)
        self.assertTrue(product.is_available)
    
    def test_product_stock_management(self):
        """Prueba gestión de stock."""
        product = Product(
            product_id=1,
            name='Test Product',
            description='A test product',
            price=99.99,
            stock=10
        )
        
        product.remove_stock(5)
        self.assertEqual(product.stock, 5)
        self.assertTrue(product.is_available)
        
        product.remove_stock(5)
        self.assertEqual(product.stock, 0)
        self.assertFalse(product.is_available)
        
        product.add_stock(1)
        self.assertEqual(product.stock, 1)
        self.assertTrue(product.is_available)
    
    def test_product_to_dict(self):
        """Prueba conversión a diccionario."""
        product = Product(
            product_id=1,
            name='Test Product',
            description='A test product',
            price=99.99,
            stock=10
        )
        
        product_dict = product.to_dict()
        self.assertIn('product_id', product_dict)
        self.assertIn('name', product_dict)
        self.assertIn('price', product_dict)
        self.assertEqual(product_dict['name'], 'Test Product')


if __name__ == '__main__':
    unittest.main()
