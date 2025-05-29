from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from ropon_auth.models import RoponUser

RoponUser = get_user_model()

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
        """Test username uniqueness constraint (after normalization)"""
        # Create first user
        RoponUser.objects.create_user(**self.user_data) # username will be 'testuser'
        
        # Attempt to create second user with same username but different email
        duplicate_data = self.user_data.copy()
        duplicate_data['email'] = 'test2@example.com'
        # duplicate_data['username'] remains 'testuser'
        
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
        """Test blank username validation (create_user)"""
        invalid_data = self.user_data.copy()
        invalid_data['username'] = ''
        
        # create_user should raise ValueError due to AbstractUser's username validation or our manager's checks
        # if username is empty after normalization.
        # If normalize_username('') results in '', AbstractUser's validation (blank=False)
        # should lead to IntegrityError on save.
        # Let's stick to testing create_user's behavior.
        with self.assertRaises((ValueError, IntegrityError)): # create_user might raise ValueError before DB hit.
            RoponUser.objects.create_user(**invalid_data)

    def test_null_username_create_user(self):
        """Test None username validation (create_user)"""
        invalid_data = self.user_data.copy()
        invalid_data['username'] = None
        invalid_data['email'] = 'noneuser@example.com' # Ensure different email
        
        with self.assertRaises((ValueError, IntegrityError)):
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

# New class for model-specific tests, especially normalization and case-insensitivity
class RoponUserModelSpecificTests(TestCase): # Renamed for clarity and to avoid clash
    """
    Tests for the RoponUser model, focusing on username case-insensitivity,
    normalization, and specific model behaviors.
    """

    def test_username_case_insensitivity_creation(self):
        """
        Tests that usernames are stored in lowercase and that creating users
        with usernames differing only by case is prevented by the database.
        """
        # Create a user with an uppercase username
        user1 = RoponUser.objects.create_user(username='TestUserAlpha', email='testuseralpha1@example.com', password='password123')
        self.assertEqual(user1.username, 'testuseralpha', "Username should be stored in lowercase.")

        # Attempt to create another user with the same username (normalized) but different case and email
        from django.db import transaction
         # Now test that creating a user with different case raises IntegrityError
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                RoponUser.objects.create_user(
                    username='testuseralpha',  # Different case
                    email='testuseralpha2@example.com', 
                    password='password123'
                )
        
        # Verify that only one user exists with that username (case-insensitively)
        self.assertEqual(RoponUser.objects.filter(username__iexact='TestUserAlpha').count(), 1)


    def test_username_case_insensitivity_retrieval(self):
        """
        Tests that users can be retrieved by username in a case-insensitive manner
        using the custom manager's get_by_natural_key method.
        """
        RoponUser.objects.create_user(username='AnotherUserBeta', email='anotheruserbeta@example.com', password='password123')
        
        # Retrieve the user with different casings
        user_lower = RoponUser.objects.get_by_natural_key('anotheruserbeta')
        user_upper = RoponUser.objects.get_by_natural_key('ANOTHERUSERBETA')
        user_mixed = RoponUser.objects.get_by_natural_key('AnotherUserBeta')

        self.assertIsNotNone(user_lower, "User should be retrievable with lowercase username.")
        self.assertIsNotNone(user_upper, "User should be retrievable with uppercase username.")
        self.assertIsNotNone(user_mixed, "User should be retrievable with mixed-case username.")
        
        self.assertEqual(user_lower, user_upper, "Retrieval with different cases should return the same user object.")
        self.assertEqual(user_lower, user_mixed, "Retrieval with different cases should return the same user object.")
        self.assertEqual(user_lower.username, 'anotheruserbeta', "Username should be stored and retrieved in lowercase.")

    def test_username_normalization_on_save(self):
        """
        Tests that if a username is somehow set to uppercase directly and saved,
        it is converted to lowercase.
        """
        user = RoponUser(username='DirectSetUserGamma', email='directgamma@example.com')
        user.password = 'password123' # Set password directly as create_user is not used here
        user.save()
        
        # Refresh from DB to ensure the save method's logic was applied
        user_from_db = RoponUser.objects.get(email='directgamma@example.com')
        self.assertEqual(user_from_db.username, 'directsetusergamma', "Username should be converted to lowercase on save.")

    def test_create_user_normalizes_username(self):
        """
        Tests that the create_user method correctly normalizes the username (strips and lowercases).
        """
        user = RoponUser.objects.create_user(username='  CreateUserTestDelta  ', email='createuserdelta@example.com', password='password123')
        self.assertEqual(user.username, 'createusertestdelta', "create_user should normalize username (strip and lowercase).")

    def test_create_superuser_normalizes_username(self):
        """
        Tests that the create_superuser method correctly normalizes the username (strips and lowercases).
        """
        admin_user = RoponUser.objects.create_superuser(username='  AdminUserTestEpsilon  ', email='adminuserepsilon@example.com', password='password123')
        self.assertEqual(admin_user.username, 'adminusertestepsilon', "create_superuser should normalize username (strip and lowercase).")

    def test_username_uniqueness_case_insensitive(self): # This is similar to test_username_case_insensitivity_creation
                                                       # but more direct.
        """
        Ensures that the database unique constraint on username (implicitly lowercase)
        prevents duplicates that only differ in case.
        """
        RoponUser.objects.create_user(username='UniqueUserZeta', email='uniquezeta1@example.com', password='password123')
        with self.assertRaises(IntegrityError):
            # This user's username 'uniqueuserzeta' will clash with 'UniqueUserZeta' (becomes 'uniqueuserzeta')
            RoponUser.objects.create_user(username='uniqueuserzeta', email='uniquezeta2@example.com', password='password123')

    def test_get_by_natural_key_nonexistent_user(self):
        """
        Tests that get_by_natural_key raises DoesNotExist for a non-existent username.
        """
        with self.assertRaises(RoponUser.DoesNotExist):
            RoponUser.objects.get_by_natural_key('NonExistentUserEta')

    def test_username_with_whitespace_normalization(self): # Renamed for clarity
        """
        Tests that usernames with leading/trailing whitespace are stripped and lowercased by create_user.
        """
        user = RoponUser.objects.create_user(username='  SpacedUserTheta  ', email='spacedtheta@example.com', password='password123')
        self.assertEqual(user.username, 'spacedusertheta', "Username should have whitespace stripped and be lowercased by create_user.")
        
        # Test retrieval with whitespace using get_by_natural_key
        retrieved_user = RoponUser.objects.get_by_natural_key('  SpacedUserTheta  ')
        self.assertEqual(retrieved_user.username, 'spacedusertheta')
        self.assertEqual(user, retrieved_user, "Retrieval with whitespace should yield the same user.")

    # test_empty_username_creation_fails_if_required from previous file is covered by
    # TestRoponUser.test_blank_username and the new TestRoponUser.test_null_username_create_user

    def test_email_is_unique_via_model_validation(self): # Slightly different from TestRoponUser.test_email_unique
                                                        # which tests create_user. This can test model's full_clean.
        """
        Test that email addresses must be unique at the model validation level.
        """
        RoponUser.objects.create_user(username='TestUserEmailKappa1', email='testkappa@example.com', password='password123')
        
        user2 = RoponUser(username='TestUserEmailKappa2', email='testkappa@example.com', password='password123')
        with self.assertRaises(ValidationError) as context: # full_clean raises ValidationError
            user2.full_clean() 
        self.assertIn('email', context.exception.message_dict)
        self.assertIn('A user with that email already exists.', context.exception.message_dict['email'])


    def test_email_is_required_on_create_user(self): # This is from the new tests
        """
        Test that email is required when using RoponUserManager.create_user.
        """
        with self.assertRaises(ValueError) as context:
            RoponUser.objects.create_user(username='NoEmailUserLambda', email=None, password='password123')
        self.assertTrue('The Email field must be set' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            RoponUser.objects.create_user(username='EmptyEmailUserLambda', email='', password='password123')
        self.assertTrue('The Email field must be set' in str(context.exception))


    def test_email_is_required_on_create_superuser(self): # This is from the new tests
        """
        Test that email is required when using RoponUserManager.create_superuser.
        """
        with self.assertRaises(ValueError) as context:
            RoponUser.objects.create_superuser(username='NoEmailSuperUserMu', email=None, password='password123')
        self.assertTrue('The Email field must be set' in str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            RoponUser.objects.create_superuser(username='EmptyEmailSuperUserMu', email='', password='password123')
        self.assertTrue('The Email field must be set' in str(context.exception))