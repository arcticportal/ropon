"""
Template tags for accessing Django settings in templates.
This provide template variables specific for ROPON application.

"""
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def frontend_url():
    """
    This tag retrieves the FRONTEND_URL setting from Django settings.
   
    """
    
    return getattr(settings, "FRONTEND_URL", None)



@register.simple_tag
def wagtail_guide_title():
    """
    Returns the Wagtail Guide menu label from wagtail_guide_settings.
    """
    
    wagtail_guide_settings = getattr(settings, "WAGTAIL_GUIDE_SETTINGS", {})
    return getattr(wagtail_guide_settings, "WAGTAIL_GUIDE_MENU_LABEL", "Editor's Guide")

@register.simple_tag
def ropon_admin_email():
    """
    Returns the email address of the ROPON admin user.
    """
    
    # Return the ROPON admin email, defaulting to 'admin@ropon.org' for consistency with settings.
    return getattr(settings, "ROPON_ADMIN_EMAIL", "admin@ropon.org")