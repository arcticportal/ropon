from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from ropon_auth.models import RoponUser

RoponUser = get_user_model()

class TestRoponUser(TestCase):
    """Consolidated tests for RoponUser model including creation, validation, and normalization"""
    
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
        """Test email uniqueness constraint at both DB and validation level"""
        # Create first user
        RoponUser.objects.create_user(**self.user_data)
        
        # Test DB-level constraint via create_user
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'testuser2'
        with self.assertRaises(IntegrityError):
            RoponUser.objects.create_user(**duplicate_data)
        
        # Test model validation level
        duplicate_user = RoponUser(username='testuser3', email=self.user_data['email'], password='pass')
        with self.assertRaisesMessage(ValidationError, 'A user with that email already exists.'):
            duplicate_user.full_clean()

    def test_username_unique_and_case_insensitive(self):
        """Test username uniqueness constraint and case-insensitivity"""
        # Create first user - username will be normalized to lowercase
        user1 = RoponUser.objects.create_user(username='TestUser', email='test1@example.com', password='pass')
        self.assertEqual(user1.username, 'testuser', "Username should be stored in lowercase")
        
        # Attempt to create with same username in different case should fail
        with self.assertRaises(IntegrityError):
            RoponUser.objects.create_user(username='testuser', email='test2@example.com', password='pass')
        
        # Verify only one user exists
        self.assertEqual(RoponUser.objects.filter(username__iexact='TestUser').count(), 1)

    def test_email_validation(self):
        """Test email validation for invalid and blank emails"""
        # Invalid email format
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid-email'
        user = RoponUser(**invalid_data)
        with self.assertRaises(ValidationError):
            user.full_clean()
        
        # Blank email
        invalid_data['email'] = ''
        user = RoponUser(**invalid_data)
        with self.assertRaises(ValidationError):
            user.full_clean()
        with self.assertRaises(ValueError):
            RoponUser.objects.create_user(**invalid_data)

    def test_blank_and_null_username(self):
        """Test blank/null username validation"""
        invalid_data = self.user_data.copy()
        
        # Blank username
        invalid_data['username'] = ''
        with self.assertRaises((ValueError, IntegrityError)):
            RoponUser.objects.create_user(**invalid_data)
        
        # Null username
        invalid_data['username'] = None
        invalid_data['email'] = 'null@example.com'
        with self.assertRaises((ValueError, IntegrityError)):
            RoponUser.objects.create_user(**invalid_data)

    def test_create_superuser(self):
        """Test superuser creation and default user permissions"""
        admin = RoponUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_active)
        
        # Test default user permissions
        user = RoponUser.objects.create_user(**self.user_data)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_username_normalization(self):
        """Test username normalization (strip whitespace and lowercase) for all creation methods"""
        # Test create_user
        user1 = RoponUser.objects.create_user(
            username='  CreateUser  ', 
            email='create@example.com', 
            password='pass'
        )
        self.assertEqual(user1.username, 'createuser')
        
        # Test create_superuser
        user2 = RoponUser.objects.create_superuser(
            username='  AdminUser  ', 
            email='admin2@example.com', 
            password='pass'
        )
        self.assertEqual(user2.username, 'adminuser')
        
        # Test direct save
        user3 = RoponUser(username='DirectUser', email='direct@example.com')
        user3.password = 'pass'
        user3.save()
        user3.refresh_from_db()
        self.assertEqual(user3.username, 'directuser')

    def test_username_case_insensitive_retrieval(self):
        """Test case-insensitive username retrieval via get_by_natural_key"""
        RoponUser.objects.create_user(username='RetrieveUser', email='retrieve@example.com', password='pass')
        
        # Retrieve with different casings
        user_lower = RoponUser.objects.get_by_natural_key('retrieveuser')
        user_upper = RoponUser.objects.get_by_natural_key('RETRIEVEUSER')
        user_mixed = RoponUser.objects.get_by_natural_key('RetrieveUser')
        user_spaced = RoponUser.objects.get_by_natural_key('  RetrieveUser  ')
        
        # All should return the same user
        self.assertEqual(user_lower, user_upper)
        self.assertEqual(user_lower, user_mixed)
        self.assertEqual(user_lower, user_spaced)
        self.assertEqual(user_lower.username, 'retrieveuser')
        
        # Test non-existent user
        with self.assertRaises(RoponUser.DoesNotExist):
            RoponUser.objects.get_by_natural_key('NonExistent')
