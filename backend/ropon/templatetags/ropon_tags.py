"""
Template tags for accessing Django settings in templates.
This provide template variables specific for ROPON application.

"""
from django import template
from django.conf import settings

from wagtail_guide.settings import wagtail_guide_settings
register = template.Library()


@register.simple_tag
def frontend_url():
    """
    Returns the frontend URL from settings.
    """
    # This tag retrieves the FRONTEND_URL setting from Django settings.
    
    return getattr(settings, "FRONTEND_URL", None)



@register.simple_tag
def wagtail_guide_title():
    """
    Returns the frontend URL from settings.
    """
    # This tag retrieves the FRONTEND_URL setting from Django settings.
    
    return getattr(wagtail_guide_settings, "WAGTAIL_GUIDE_MENU_LABEL", "Editor's Guide")

