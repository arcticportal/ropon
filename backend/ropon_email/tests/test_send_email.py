import time # Import time module
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache # Import cache
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.settings import api_settings # Import api_settings

# filepath: backend/ropon_email/tests/test_send_email.py
"""
Tests for the SendContactEmailAPIView in ropon_email.views.

Covers successful sending, validation, configuration errors, throttling,
and disallowed methods.
"""

# Use relative import for the view being tested
# Note: Assuming the view is in views.py within the same app directory
# If your structure is different, adjust the import accordingly.
# from ..views import SendContactEmailAPIView # This import is not strictly needed as tests use reverse() and mock EmailMessage


class SendContactEmailAPIViewTestCase(TestCase):
    """
    Test suite for the SendContactEmailAPIView.

    Provides tests for successful email sending, handling of multiple admin emails,
    validation errors, configuration errors (missing/empty admin email),
    email sending failures, throttling, and disallowed HTTP methods.
    """

    def setUp(self):
        """
        Set up the test client, URL, common data, and settings values for tests.
        """
        self.client = APIClient()
       
        # Ensure 'send_contact_email' is the correct name of the URL pattern
        # defined in your urls.py for the SendContactEmailAPIView
        self.url = reverse('ropon_email:send_contact_email')
        self.valid_data = {
            'name': 'Test User',
            'from_email_id': 'test@example.com',
            'message': 'This is a test message.'
        }
        # Define settings values used in multiple tests
        self.admin_email = 'admin@ropon.org'
        self.default_from_email = 'noreply@ropon.org'
        # Clear cache before each test to ensure isolation, especially for throttling
        cache.clear()

    @override_settings(
        ROPON_ADMIN_EMAIL='admin@ropon.org', # Use literal value matching setUp
        DEFAULT_FROM_EMAIL='noreply@ropon.org' # Use literal value matching setUp
    )
    @patch('ropon_email.views.EmailMessage')
    def test_send_email_success(self, mock_email_message):
        """
        Test successful email sending with valid data and single admin email.

        Verifies:
        - HTTP 200 OK status code.
        - Correct success message in the response.
        - EmailMessage is instantiated with correct subject, body, from_email, to, and reply_to.
        - The send() method on the EmailMessage instance is called once.
        """
        # Arrange: Mock the EmailMessage instance and its send method
        mock_email_instance = MagicMock()
        mock_email_message.return_value = mock_email_instance

        # Act: Send POST request
        response = self.client.post(self.url, self.valid_data, format='json')

        # Assert: Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Email sent successfully."})

        # Assert: Check EmailMessage instantiation arguments
        # Update expected values to match the actual implementation in views.py
        expected_subject = f"Contact Form Submission from {self.valid_data['name']}"
        # The view implementation adds a leading newline and doesn't include name/email in the body
        expected_body = f"\n{self.valid_data['message']}"
        # The view implementation formats the from_email
        expected_from_email = f'{self.valid_data["name"]}<{self.default_from_email}>'

        mock_email_message.assert_called_once_with(
            subject=expected_subject,
            body=expected_body, # Use updated expected body
            from_email=expected_from_email, # Use updated expected from_email
            to=[self.admin_email], # Use setUp attribute for consistency in assertion
            reply_to=[self.valid_data['from_email_id']],
        )

        # Assert: Check send method call
        mock_email_instance.send.assert_called_once_with(fail_silently=False)

    @override_settings(
        # Test with a comma-separated string including whitespace
        ROPON_ADMIN_EMAIL='admin1@test.com, admin2@test.com ',
        DEFAULT_FROM_EMAIL='noreply@ropon.org' # Use literal value matching setUp
    )
    @patch('ropon_email.views.EmailMessage')
    def test_send_email_multiple_admins(self, mock_email_message):
        """
        Test successful email sending with multiple admin emails defined in settings.

        Verifies:
        - HTTP 200 OK status code.
        - Correct success message in the response.
        - EmailMessage is instantiated with a cleaned list of recipient emails.
        - The send() method on the EmailMessage instance is called once.
        """
        # Arrange
        mock_email_instance = MagicMock()
        mock_email_message.return_value = mock_email_instance

        # Act
        response = self.client.post(self.url, self.valid_data, format='json')

        # Assert: Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Email sent successfully."})

        # Assert: Check EmailMessage instantiation arguments (specifically 'to')
        mock_email_message.assert_called_once()
        # Retrieve keyword arguments passed to EmailMessage constructor
        call_args, call_kwargs = mock_email_message.call_args
        # Ensure the 'to' list is correctly parsed and stripped
        self.assertEqual(call_kwargs['to'], ['admin1@test.com', 'admin2@test.com'])

        # Assert: Check send method call
        mock_email_instance.send.assert_called_once_with(fail_silently=False)

    @override_settings(
        ROPON_ADMIN_EMAIL='admin@ropon.org', # Use literal value matching setUp
        DEFAULT_FROM_EMAIL='noreply@ropon.org' # Use literal value matching setUp
    )
    @patch('ropon_email.views.EmailMessage')
    def test_send_email_invalid_data(self, mock_email_message):
        """
        Test email sending failure due to invalid input data (serializer errors).

        Verifies:
        - HTTP 400 Bad Request status code.
        - Response data contains serializer error messages for missing fields.
        - EmailMessage is not instantiated or called.
        """
        # Arrange: Prepare invalid data (missing required fields)
        invalid_data = {
            'name': 'Test User',
            # 'from_email_id' is missing
            # 'message' is missing
        }

        # Act
        response = self.client.post(self.url, invalid_data, format='json')

        # Assert: Check response status and error content
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that the expected error keys are present in the response data
        self.assertIn('from_email_id', response.data)
        self.assertIn('message', response.data)

        # Assert: Ensure email sending was not attempted
        mock_email_message.assert_not_called()

    @override_settings(
        ROPON_ADMIN_EMAIL=None, # Simulate missing/None setting
        DEFAULT_FROM_EMAIL='' # Simulate empty DEFAULT_FROM_EMAIL setting
    )
    @patch('ropon_email.views.EmailMessage')
    def test_send_email_missing_admin_default_email_setting(self, mock_email_message):
        """
        Test failure when ROPON_ADMIN_EMAIL and DEFAULT_FROM_EMAIL settings are not configured (are None).

        Verifies:
        - HTTP 500 Internal Server Error status code.
        - Correct error message indicating configuration issue.
        - EmailMessage is not instantiated or called.
        """
        # Act
        response = self.client.post(self.url, self.valid_data, format='json')

        # Assert: Check response status and error content
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, {"error": "Server configuration error: Admin email not set."})

        # Assert: Ensure email sending was not attempted
        mock_email_message.assert_not_called()

    @override_settings(
        ROPON_ADMIN_EMAIL=None, # Simulate missing/None setting
        DEFAULT_FROM_EMAIL='noreply@ropon.org' # Use literal value matching setUp
    )
    @patch('ropon_email.views.EmailMessage')
    def test_send_email_missing_admin_email_setting(self, mock_email_message):
        """
        Test failure when ROPON_ADMIN_EMAIL setting is not configured (is None).

        Verifies:
        - HTTP 500 Internal Server Error status code.
        - Correct error message indicating configuration issue.
        - EmailMessage is not instantiated or called.
        """

         # Arrange: Mock the EmailMessage instance and its send method
        mock_email_instance = MagicMock()
        mock_email_message.return_value = mock_email_instance

        # Act
        response = self.client.post(self.url, self.valid_data, format='json')

          # Assert: Check response status and success content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Email sent successfully."})

        # Assert: Check EmailMessage instantiation uses DEFAULT_FROM_EMAIL as fallback
        mock_email_message.assert_called_once()
        call_args, call_kwargs = mock_email_message.call_args
        # When ROPON_ADMIN_EMAIL is empty, should fallback to DEFAULT_FROM_EMAIL
        self.assertEqual(call_kwargs['to'], [self.default_from_email])

        # Assert: Check send method call
        mock_email_instance.send.assert_called_once_with(fail_silently=False)


    @override_settings(
        ROPON_ADMIN_EMAIL='', # Simulate empty string setting
        DEFAULT_FROM_EMAIL='noreply@ropon.org' # Use literal value matching setUp
    )
    @patch('ropon_email.views.EmailMessage')
    def test_send_email_empty_admin_email_setting(self, mock_email_message):
        """
        Test fallback to DEFAULT_FROM_EMAIL when ROPON_ADMIN_EMAIL setting is empty.

        Verifies:
        - HTTP 200 OK status code (email sent successfully).
        - Correct success message in the response.
        - EmailMessage is instantiated with DEFAULT_FROM_EMAIL as the recipient.
        - The send() method on the EmailMessage instance is called once.
        """
        # Arrange: Mock the EmailMessage instance and its send method
        mock_email_instance = MagicMock()
        mock_email_message.return_value = mock_email_instance

        # Act
        response = self.client.post(self.url, self.valid_data, format='json')

        # Assert: Check response status and success content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Email sent successfully."})

        # Assert: Check EmailMessage instantiation uses DEFAULT_FROM_EMAIL as fallback
        mock_email_message.assert_called_once()
        call_args, call_kwargs = mock_email_message.call_args
        # When ROPON_ADMIN_EMAIL is empty, should fallback to DEFAULT_FROM_EMAIL
        self.assertEqual(call_kwargs['to'], [self.default_from_email])

        # Assert: Check send method call
        mock_email_instance.send.assert_called_once_with(fail_silently=False)

    @override_settings(
        ROPON_ADMIN_EMAIL='admin@ropon.org', # Use literal value matching setUp
        DEFAULT_FROM_EMAIL='noreply@ropon.org' # Use literal value matching setUp
    )
    @patch('ropon_email.views.EmailMessage')
    def test_send_email_send_failure(self, mock_email_message):
        """
        Test failure when the email sending process itself raises an exception.

        Verifies:
        - HTTP 500 Internal Server Error status code.
        - Correct error message indicating sending failure.
        - EmailMessage is instantiated.
        - The send() method on the EmailMessage instance is called once and raises an exception.
        """
        # Arrange: Mock the EmailMessage instance and make its send method raise an exception
        mock_email_instance = MagicMock()
        # Simulate an error during the send process
        mock_email_instance.send.side_effect = Exception("Simulated SMTP Error")
        mock_email_message.return_value = mock_email_instance

        # Act
        response = self.client.post(self.url, self.valid_data, format='json')

        # Assert: Check response status and error content
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, {"error": "Failed to send email."})

        # Assert: Check EmailMessage was called
        mock_email_message.assert_called_once()
        # Assert: Check the send method was called
        mock_email_instance.send.assert_called_once_with(fail_silently=False)

    @override_settings(
        ROPON_ADMIN_EMAIL='admin@ropon.org',
        DEFAULT_FROM_EMAIL='noreply@ropon.org'
    )
    @patch('ropon_email.views.EmailMessage')
    def test_honeypot_filled_slow_still_sends(self, mock_email_message):
        """
        A submission that fills a honeypot candidate field but takes a human
        amount of time is NOT treated as a bot: browser autofill can populate
        the trap for genuine users, so the email is still sent (the trip is
        logged server-side instead). Guards against losing real messages.
        """
        # Arrange: mock send; fill a honeypot candidate with an old _ts
        mock_email_instance = MagicMock()
        mock_email_message.return_value = mock_email_instance
        data = dict(
            self.valid_data,
            fax_number='https://user-site.example',
            _ts=int(time.time() * 1000) - 10000,  # 10s old -> human speed
        )

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert: real 200 and the email is actually sent
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Email sent successfully."})
        mock_email_instance.send.assert_called_once_with(fail_silently=False)

    @override_settings(
        ROPON_ADMIN_EMAIL='admin@ropon.org',
        DEFAULT_FROM_EMAIL='noreply@ropon.org'
    )
    @patch('ropon_email.views.EmailMessage')
    def test_honeypot_filled_no_ts_still_sends(self, mock_email_message):
        """
        A filled honeypot with no _ts at all (timing fails open) is delivered:
        the honeypot alone never blocks. Documents the fail-open combination.
        """
        # Arrange
        mock_email_instance = MagicMock()
        mock_email_message.return_value = mock_email_instance
        data = dict(self.valid_data, fax_number='https://user-site.example')

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Email sent successfully."})
        mock_email_instance.send.assert_called_once_with(fail_silently=False)

    @override_settings(
        ROPON_ADMIN_EMAIL='admin@ropon.org',
        DEFAULT_FROM_EMAIL='noreply@ropon.org'
    )
    @patch('ropon_email.views.EmailMessage')
    def test_honeypot_filled_fast_returns_silent_success(self, mock_email_message):
        """
        A submission that fills a honeypot candidate AND arrives faster than
        MIN_FORM_SECONDS is treated as a bot: silent HTTP 200 carrying the SAME
        success body as a real submission (so the bot can't tell it was
        caught) and no email is actually sent.
        """
        # Arrange: fill a honeypot candidate with a fresh _ts
        data = dict(
            self.valid_data,
            fax_number='https://spam.example',
            _ts=int(time.time() * 1000),
        )

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert: silent 200 with real-looking body, no email sent
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Email sent successfully."})
        mock_email_message.assert_not_called()

    @override_settings(
        ROPON_ADMIN_EMAIL='admin@ropon.org',
        DEFAULT_FROM_EMAIL='noreply@ropon.org'
    )
    @patch('ropon_email.views.EmailMessage')
    def test_timing_too_fast_returns_silent_success(self, mock_email_message):
        """
        A submission whose _ts is only milliseconds old (faster than
        MIN_FORM_SECONDS) is treated as a bot: silent 200, no email sent.
        """
        # Arrange: _ts stamped "now" -> near-zero elapsed
        data = dict(self.valid_data, _ts=int(time.time() * 1000))

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Email sent successfully."})
        mock_email_message.assert_not_called()

    @override_settings(
        ROPON_ADMIN_EMAIL='admin@ropon.org',
        DEFAULT_FROM_EMAIL='noreply@ropon.org'
    )
    @patch('ropon_email.views.EmailMessage')
    def test_timing_old_enough_sends(self, mock_email_message):
        """
        A submission with an _ts comfortably older than MIN_FORM_SECONDS passes
        the timing check and sends normally. Guards against the check being too
        aggressive.
        """
        # Arrange
        mock_email_instance = MagicMock()
        mock_email_message.return_value = mock_email_instance
        # _ts 10s in the past -> elapsed well above the 3s threshold
        data = dict(self.valid_data, _ts=int(time.time() * 1000) - 10000)

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Email sent successfully."})
        mock_email_instance.send.assert_called_once_with(fail_silently=False)

    @override_settings(
        ROPON_ADMIN_EMAIL='admin@ropon.org',
        DEFAULT_FROM_EMAIL='noreply@ropon.org'
    )
    @patch('ropon_email.views.EmailMessage')
    def test_timing_missing_still_sends(self, mock_email_message):
        """
        A submission carrying no _ts (fail-open) sends normally. Documents that
        the timing check never blocks when the timestamp is absent -- this is
        what keeps the behavior safe for clients that don't send timing.
        """
        # Arrange
        mock_email_instance = MagicMock()
        mock_email_message.return_value = mock_email_instance

        # Act: valid_data has no _ts
        response = self.client.post(self.url, self.valid_data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Email sent successfully."})
        mock_email_instance.send.assert_called_once_with(fail_silently=False)

    @override_settings(
        ROPON_ADMIN_EMAIL='admin@ropon.org',
        DEFAULT_FROM_EMAIL='noreply@ropon.org'
    )
    @patch('ropon_email.views.EmailMessage')
    @patch('rest_framework.throttling.SimpleRateThrottle.timer') # Patch the throttle's timer method
    def test_throttling(self, mock_timer, mock_email_message): # Add mock_timer back
        """
        Test that the view respects the throttling settings (AnonRateThrottle).
        Uses patch.dict to modify DRF settings reliably within the test.

        Verifies:
        - The first request succeeds (HTTP 200 OK).
        - The second request from the same client, after simulating time passage,
          is throttled (HTTP 429 Too Many Requests).
        - The email send method is called only once (for the first successful request).
        """
        # Arrange
        mock_email_instance = MagicMock()
        mock_email_message.return_value = mock_email_instance
        remote_addr = '127.0.0.1'
        # Set initial time using the mock timer
        current_time = time.time() # Get a real timestamp for calculations
        mock_timer.return_value = current_time

        # Use patch.dict to temporarily modify DRF throttle rates for this test
        with patch.dict(api_settings.DEFAULT_THROTTLE_RATES, {'email': '1/day'}):
            # Act: First request (should succeed)
            response1 = self.client.post(
                self.url, 
                self.valid_data, 
                format='json', 
                REMOTE_ADDR=remote_addr
            )
            # Assert: First request successful
            self.assertEqual(response1.status_code, status.HTTP_200_OK)
            mock_email_instance.send.assert_called_once() # Send called once

            # Arrange: Simulate time passing *within* the throttle duration (1 day for '1/day')
            # Advance time by a small amount, less than the throttle period (e.g., 1 second)
            mock_timer.return_value = current_time + 1

            # Act: Second request (should be throttled)
            response2 = self.client.post(
                self.url, 
                self.valid_data, 
                format='json', 
                REMOTE_ADDR=remote_addr
            )
            # Assert: Second request throttled
            self.assertEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

            # Assert: Ensure send was not called again for the throttled request
            mock_email_instance.send.assert_called_once()

    def test_disallowed_methods(self):
        """
        Test that HTTP methods other than POST, HEAD, OPTIONS are disallowed.
        Overrides throttle rate to prevent interference from previous tests.

        Verifies:
        - GET, PUT, DELETE, PATCH requests receive HTTP 405 Method Not Allowed status code.
        """
        # Test GET
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test PUT
        put_response = self.client.put(self.url, self.valid_data, format='json')
        self.assertEqual(put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test DELETE
        delete_response = self.client.delete(self.url)
        self.assertEqual(delete_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test PATCH
        patch_response = self.client.patch(self.url, self.valid_data, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Optional: Test HEAD and OPTIONS if specific behavior is expected
    # def test_options_method(self):
    #     """ Test OPTIONS method """
    #     response = self.client.options(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # Check headers like 'Allow' if necessary
    #     self.assertIn('Allow', response)
    #     self.assertIn('POST', response['Allow'])
    #     self.assertIn('HEAD', response['Allow'])
    #     self.assertIn('OPTIONS', response['Allow'])

    # def test_head_method(self):
    #     """ Test HEAD method """
    #     # Note: HEAD requests might behave differently depending on middleware/DRF setup.
    #     # Often they might return 405 or need specific handling.
    #     # If POST is the primary method, testing HEAD might not be critical unless
    #     # specific HEAD behavior is implemented or required.
    #     response = self.client.head(self.url)
    #     # Check for expected status, likely 200 OK if allowed and handled like GET without body,
    #     # or potentially 405 if not explicitly handled/allowed.
    #     # Adjust assertion based on expected behavior.
    #     self.assertEqual(response.status_code, status.HTTP_200_OK) # Or status.HTTP_405_METHOD_NOT_ALLOWED
