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
    Returns the frontend URL from settings.
    """
    # This tag retrieves the FRONTEND_URL setting from Django settings.
    
    return getattr(settings, "FRONTEND_URL", None)

