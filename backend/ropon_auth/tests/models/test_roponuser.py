from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from ropon_auth.models import RoponUser

class TestRoponUser(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_create_user_success(self):
        """Test successful user creation with valid data"""
        user = RoponUser.objects.create_user(**self.user_data)
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_email_unique(self):
        """Test email uniqueness constraint"""
        # Create first user
        RoponUser.objects.create_user(**self.user_data)
        
        # Attempt to create second user with same email
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'testuser2'
        
        with self.assertRaises(IntegrityError):
            RoponUser.objects.create_user(**duplicate_data)

    def test_username_unique(self):
        """Test username uniqueness constraint"""
        # Create first user
        RoponUser.objects.create_user(**self.user_data)
        
        # Attempt to create second user with same username
        duplicate_data = self.user_data.copy()
        duplicate_data['email'] = 'test2@example.com'
        
        with self.assertRaises(IntegrityError):
            RoponUser.objects.create_user(**duplicate_data)

    def test_invalid_email(self):
        """Test invalid email format validation"""
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        user = RoponUser(**invalid_data)
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_blank_email(self):
        """Test blank email validation"""
        invalid_data = self.user_data.copy()
        invalid_data['email'] = ''

        user = RoponUser(**invalid_data)
        with self.assertRaises(ValidationError):
            user.full_clean()
    
        with self.assertRaises(ValueError):
            RoponUser.objects.create_user(**invalid_data)

    def test_blank_username(self):
        """Test blank username validation"""
        invalid_data = self.user_data.copy()
        invalid_data['username'] = ''
        
        with self.assertRaises(ValueError):
            RoponUser.objects.create_user(**invalid_data)

    def test_custom_email_error_message(self):
        """Test custom error message for duplicate email"""
        # Create first user
        RoponUser.objects.create_user(**self.user_data)
        
        # Create second user with same email
        duplicate_user = RoponUser(**{
            'username': 'testuser2',
            'email': self.user_data['email'],
            'password': 'securepass123'
        })
        
        with self.assertRaisesMessage(ValidationError, 'A user with that email already exists.'):
            duplicate_user.full_clean()

    def test_create_superuser(self):
        """Test superuser creation and permissions"""
        admin = RoponUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_active)

    def test_default_user_permissions(self):
        """Test default user permissions"""
        user = RoponUser.objects.create_user(**self.user_data)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)