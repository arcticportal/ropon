from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test.client import RequestFactory

# Import the hook function we want to test
from ropon_auth.wagtail_hooks import send_welcome_email_on_user_create

RoponUser = get_user_model()

class TestUserCreationEmailHook(TestCase):
    def setUp(self):
        """Set up common test resources."""
        self.factory = RequestFactory()
        # Create a user who needs to set their password
        self.user = RoponUser.objects.create_user(
            username='neweditor',
            email='neweditor@example.com',
            password=None  # Explicitly no password set
        )

        # Define common settings for email generation to ensure consistency
        self.expected_settings = {
            'DEFAULT_FROM_EMAIL': 'noreply@ropon.example.com',
            'WAGTAILADMIN_BASE_URL': 'http://admin.ropon.example.com',
            'FRONTEND_URL': 'http://portal.ropon.example.com',
            'ROPON_ADMIN_EMAIL': 'contact@ropon.example.com'
        }

    @override_settings() # Decorator to ensure settings are reset after the test
    def test_hook_function_sends_correct_email(self):
        """
        Test that the send_welcome_email_on_user_create function (the hook's action)
        sends an email with the correct details when invoked directly.
        """
        # Override Django settings for the duration of this test
        with override_settings(
            DEFAULT_FROM_EMAIL=self.expected_settings['DEFAULT_FROM_EMAIL'],
            WAGTAILADMIN_BASE_URL=self.expected_settings['WAGTAILADMIN_BASE_URL'],
            FRONTEND_URL=self.expected_settings['FRONTEND_URL'],
            ROPON_ADMIN_EMAIL=self.expected_settings['ROPON_ADMIN_EMAIL']
        ):
            # Create a mock request object, as the hook function expects it.
            # The scheme and host might be used if WAGTAILADMIN_BASE_URL is not set.
            request = self.factory.get('/fake-admin-path-for-request')

            # Manually call the hook function, simulating Wagtail's invocation after user creation
            send_welcome_email_on_user_create(request, self.user)

            # 1. Check that one email has been sent
            self.assertEqual(len(mail.outbox), 1, "One email should be sent.")
            email_message = mail.outbox[0]

            # 2. Check recipient and sender
            self.assertEqual(email_message.to, [self.user.email], "Email sent to incorrect recipient.")
            self.assertEqual(email_message.from_email, self.expected_settings['DEFAULT_FROM_EMAIL'], "Email sent from incorrect sender.")

            # 3. Check subject (content is rendered from WELCOME_EMAIL_SUBJECT_TEMPLATE)
            # We expect key phrases rather than exact match due to potential translations.
            self.assertIn("ROPON", email_message.subject, "Subject missing project name.")
            self.assertIn("Set Your Password", email_message.subject, "Subject missing key action phrase.")

            # 4. Check body content (content is rendered from WELCOME_EMAIL_BODY_TEMPLATE)
            body = email_message.body
            self.assertIn(self.user.username, body, "Username missing from email body.")
            self.assertIn(self.expected_settings['FRONTEND_URL'], body, "Frontend URL missing from email body.")
            self.assertIn(self.expected_settings['ROPON_ADMIN_EMAIL'], body, "ROPON admin email missing from email body.")
            
            # 5. Check for the reset URL structure
            # The exact token and uid are dynamic, so we check for the base URL and path structure.
            self.assertIn(self.expected_settings['WAGTAILADMIN_BASE_URL'], body, "WAGTAILADMIN_BASE_URL missing from reset link.")
            # Check for the path segment that reverse('password_reset_confirm', ...) would generate part of.
            # We can't match the full token/uid, but the path structure should be there.
            # Example: /reset/<uidb64>/<token>/
            self.assertRegex(body, r'reset/[^/]+/[^/]+/', "Password reset URL structure not found in email body.")

    @override_settings() # Decorator to ensure settings are reset
    def test_email_uses_request_scheme_host_if_base_url_not_set(self):
        """
        Test that the email sending falls back to request.scheme and request.get_host()
        if WAGTAILADMIN_BASE_URL is not set (i.e., None).
        """
        with override_settings(
            DEFAULT_FROM_EMAIL=self.expected_settings['DEFAULT_FROM_EMAIL'],
            FRONTEND_URL=self.expected_settings['FRONTEND_URL'],
            ROPON_ADMIN_EMAIL=self.expected_settings['ROPON_ADMIN_EMAIL'],
            WAGTAILADMIN_BASE_URL=None # Explicitly simulate WAGTAILADMIN_BASE_URL not being set
        ):
            # Create a mock request, specifying scheme (e.g., https) and host
            # Note: RequestFactory default host is 'testserver'
            request = self.factory.get('/fake-admin-path', secure=True) # secure=True sets scheme to 'https'
            expected_base_from_request = f"https://{request.get_host()}" # e.g., "https://testserver"

            send_welcome_email_on_user_create(request, self.user)

            self.assertEqual(len(mail.outbox), 1, "One email should be sent.")
            email_message = mail.outbox[0]

            # Check that the reset URL in the body uses the scheme and host from the request
            self.assertIn(expected_base_from_request, email_message.body, 
                          "Email body does not use request scheme/host when WAGTAILADMIN_BASE_URL is not set.")
            self.assertRegex(email_message.body, r'reset/[^/]+/[^/]+/', 
                             "Password reset URL structure not found in email body with fallback base URL.")

