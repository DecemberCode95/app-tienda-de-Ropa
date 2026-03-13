from django.test import TestCase
from django.contrib.auth.models import User
from shop.models import Category, Product


class CategoryModelTest(TestCase):
    """
    Test cases for Category model.
    """
    
    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic devices'
        )
    
    def test_category_creation(self):
        """Test category creation."""
        self.assertEqual(self.category.name, 'Electronics')
        self.assertEqual(self.category.slug, 'electronics')
    
    def test_category_str(self):
        """Test category string representation."""
        self.assertEqual(str(self.category), 'Electronics')


class ProductModelTest(TestCase):
    """
    Test cases for Product model.
    """
    
    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(
            name='Laptops',
            slug='laptops'
        )
        self.product = Product.objects.create(
            name='Test Laptop',
            slug='test-laptop',
            category=self.category,
            description='A test laptop',
            price=999.99,
            stock=10
        )
    
    def test_product_creation(self):
        """Test product creation."""
        self.assertEqual(self.product.name, 'Test Laptop')
        self.assertEqual(self.product.price, 999.99)
        self.assertEqual(self.product.stock, 10)
    
    def test_product_in_stock(self):
        """Test if product is in stock."""
        self.assertTrue(self.product.stock > 0)
    
    def test_product_str(self):
        """Test product string representation."""
        self.assertEqual(str(self.product), 'Test Laptop')
