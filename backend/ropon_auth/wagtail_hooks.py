from wagtail import hooks
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging
          
# Template paths as constants
WELCOME_EMAIL_SUBJECT_TEMPLATE = 'ropon_auth/new_user_email/welcome_subject.txt'
WELCOME_EMAIL_BODY_TEMPLATE = 'ropon_auth/new_user_email/welcome_body.txt'


@hooks.register('after_create_user')
def send_welcome_email_on_user_create(request, user):
    """
    Sends a password reset email to a new user after they are created via Wagtail admin.
    This function is connected to Wagtail's 'after_create_user' hook.

    Args:
        request: The HttpRequest object.
        user: The user instance that has just been created.
    """
    if user.email: # Check if the user has an email
        # Generate token and uid for password reset
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Get WAGTAILADMIN_BASE_URL from settings, default to None
        base_url = getattr(settings, 'WAGTAILADMIN_BASE_URL', None)
        
        reset_path = reverse('wagtailadmin_password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        if base_url:
            # Ensure no double slashes if base_url has a trailing slash and reset_path has a leading one
            reset_url = f"{base_url.rstrip('/')}{reset_path}"
        else:
            # Fallback to using request scheme and host if WAGTAILADMIN_BASE_URL is not set
            scheme = request.scheme
            domain = request.get_host()
            reset_url = f"{scheme}://{domain}{reset_path}"
        
        # Get FRONTEND_URL from settings, default to None
        frontend_url = getattr(settings, 'FRONTEND_URL', None)

        # Get ROPON_ADMIN_EMAIL from settings, default to DEFAULT_FROM_EMAIL
        # getattr handles if ROPON_ADMIN_EMAIL is not defined.
        # Then, check if the retrieved value is empty and default if so.
        ropon_admin_email = getattr(settings, 'ROPON_ADMIN_EMAIL', None)
        if not ropon_admin_email: # Handles None or empty string
            ropon_admin_email = settings.DEFAULT_FROM_EMAIL # Assumes DEFAULT_FROM_EMAIL is always set

        context = {
            'user': user,
            'reset_url': reset_url,
            'frontend_url': frontend_url,
            'ropon_admin_email': ropon_admin_email,
        }

        # Render subject and body from templates
        subject = render_to_string(WELCOME_EMAIL_SUBJECT_TEMPLATE, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        
        body = render_to_string(WELCOME_EMAIL_BODY_TEMPLATE, context)
        
        # Use the standard settings.DEFAULT_FROM_EMAIL for the sender of this specific email
        from_email = settings.DEFAULT_FROM_EMAIL 
        recipient_list = [user.email]

        try:
            send_mail(subject, body, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            # Consider using Django's logging framework for production
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send welcome email to {user.email}: {e}")

