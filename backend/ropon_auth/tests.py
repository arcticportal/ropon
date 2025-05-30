from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model

RoponUser = get_user_model()

class RoponUserModelTest(TestCase):
    def setUp(self):
        """Set up test users."""
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        # Ensure the password_reset_confirm URL is available for the email
        # This might require setting up a dummy URLconf for tests if not already present
        # For simplicity, we assume it's available.

    def test_create_user_sends_email(self):
        """Test that an email is sent when a new user is created."""
        # Create a new user
        user = RoponUser.objects.create_user(**self.user_data)

        # Check that one email has been sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Get the email
        email = mail.outbox[0]

        # Check the recipient, subject, and body (partially)
        self.assertEqual(email.to, [self.user_data['email']])
        self.assertEqual(email.subject, 'Welcome to ROPON - Set Your Password')
        
        # Check for the presence of the username and reset link in the email body
        self.assertIn(self.user_data['username'], email.body)
        
        # Construct the expected part of the reset URL
        # Note: uid and token will be specific to this user creation,
        # so we can't match the exact URL, but we can check for its components.
        # We need to ensure 'password_reset_confirm' is a valid reverse match.
        # This might require ensuring your project's URLconf is loaded,
        # or mocking reverse if it's problematic in isolated tests.
        self.assertIn(f"Hi {self.user_data['username']}", email.body)
        self.assertIn("Please set your password by clicking the link below:", email.body)
        self.assertIn(f"You will be asked to enter this email address ({self.user_data['email']})", email.body)

        # To check the reset link more thoroughly, you might need to:
        # 1. Mock default_token_generator and urlsafe_base64_encode to predict their output
        # 2. Or, parse the link from the email body and attempt to resolve it (more complex)
        # For this test, we'll check that a URL containing 'reset' is present.
        self.assertIn('/reset/', email.body) # A basic check for the reset path
