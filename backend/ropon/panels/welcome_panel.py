"""
RoPON Welcome Panel

This module contains the welcome panel component for the Wagtail admin homepage.
"""
from wagtail.admin.ui.components import Component


class RoponWelcomePanel(Component):
    """
    Welcome panel component for the Wagtail admin homepage.
    
    This panel provides basic navigation and information for RoPON administrators,
    appearing immediately after the top heading panel on the admin homepage.
    
    The panel uses a Django template to separate content from code, allowing for
    easy content management and internationalization. It uses the existing
    frontend_url template tag to avoid adding custom context variables.
    """
    template_name = 'ropon/panels/welcome_panel.html'
    order = 150  # Positioned after standard panels but before custom content panels
    
    def get_context_data(self, parent_context):
        """
        Prepare context data for the template.
        
        Args:
            parent_context (dict): Context from the calling template
            
        Returns:
            dict: Context data for the template (no custom variables needed)
        """
        context = super().get_context_data(parent_context)
        # No additional context needed - template uses frontend_url tag
        return context
