"""
API Views for the ropon_email app.
"""
from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status # Import permissions
from rest_framework.throttling import AnonRateThrottle
from .serializers import ContactFormSerializer

class ContactFormEmailThrottle(AnonRateThrottle):
    """
    Custom throttle scope for the contact form endpoint.
    Uses the 'email' rate defined in settings.
    """
    scope = 'email' # Changed from 'anon' to 'email'

class SendContactEmailAPIView(APIView):
    """
    API View to handle sending emails from the contact form.
    Inherits from DRF's APIView.

    Accepts POST requests with 'name', 'from_email_id', and 'message'.
    Validates the input and sends an email to the ROPON admin email,
    setting the Reply-To header to the sender's email.
    Applies rate limiting to prevent abuse.
    """
    # Allow any user (authenticated or anonymous) to access this view
    # permission_classes = [permissions.AllowAny]
    throttle_classes = [ContactFormEmailThrottle]

    http_method_names = ['post', 'head', 'options']

    def post(self, request, *args, **kwargs):
        """
        Handles POST request to send contact form email.

        Args:
            request: The HTTP request object containing form data.

        Returns:
            Response: JSON response indicating success or failure.
        """
        serializer = ContactFormSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            reply_to_email = serializer.validated_data['from_email_id']
            message_body = serializer.validated_data['message']

            subject = f"Contact Form Submission from {name}"
            full_message = f"\n{message_body}"
            # Get recipient email(s) from ROPON_ADMIN_EMAIL setting
            # If set as comma-separated list, parse and clean each email
            recipient_list = []
            if hasattr(settings, 'ROPON_ADMIN_EMAIL') and settings.ROPON_ADMIN_EMAIL:
                if isinstance(settings.ROPON_ADMIN_EMAIL, str):
                    recipient_list = [email.strip() for email in settings.ROPON_ADMIN_EMAIL.split(',') if email.strip()]
            
            if not recipient_list:
                print("Error: ROPON_ADMIN_EMAIL is not configured properly.")
                return Response({"error": "Server configuration error: Admin email not set."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                # Format the from_email to include the sender's name
                from_email = f'{name}<{settings.DEFAULT_FROM_EMAIL}>'
                
                email = EmailMessage(
                    subject=subject,
                    body=full_message,
                    from_email=from_email,
                    to=recipient_list,
                    reply_to=[reply_to_email],
                )
                email.send(fail_silently=False)

                return Response({"message": "Email sent successfully."}, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"Error sending email: {e}")
                return Response({"error": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
