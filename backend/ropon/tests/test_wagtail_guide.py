from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from wagtail.admin.menu import MenuItem, help_menu, admin_menu
from django.core.cache import cache
from wagtail_guide.settings import wagtail_guide_settings

# Define the User model through Django's get_user_model
User = get_user_model()


class WagtailGuideTest(TestCase):
    """
    Tests for the wagtail_guide package integration with feature flags
    and custom settings.
    
    Tests verify:
    - Feature flag behavior for enabling/disabling the guide
    - Guide accessibility
    - Behavior with different user roles (Moderators vs superuser)
    """
    
    def setUp(self):
        """
        Set up the test environment with users and initial data.
        
        Creates both admin user and moderator user, and creates the Moderators group.
        """

        super().setUp()

        cache.clear()
        # Create the Moderators group
        self.moderators_group, _ = Group.objects.get_or_create(name='Moderators')
        
        # Create admin user
        self.admin_user = self.create_admin_user()
        
        # Create moderator user
        self.moderator_user = self.create_moderator_user()
        
        # Common URLs
        self.admin_home_url = reverse('wagtailadmin_home')
        self.guide_url = reverse('wagtaileditorguide')
        
        # Clear the cache to ensure fresh data for each test

    def tearDown(self):
        """
        Clean up after each test to ensure isolation.
        """
        # Clear the cached menu items to prevent test interference
        if hasattr(admin_menu, '_registered_menu_items'):
            delattr(admin_menu, '_registered_menu_items')
        if hasattr(help_menu, '_registered_menu_items'):
            delattr(help_menu, '_registered_menu_items')

    def create_admin_user(self):
        """
        Create and return a superuser for testing admin features.
        
        Returns:
            User: A superuser for admin testing
        """
        # Use the get_user_model() result instead of direct model reference
        return User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
    
    def create_moderator_user(self):
        """
        Create and return a standard user in the Moderators group.
        
        Returns:
            User: A standard user with Moderator permissions
        """
        # Create a standard user
        user = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='password',
            is_staff=True  # Staff status needed to access admin
        )
        
        # Add user to the Moderators group
        user.groups.add(self.moderators_group)
        
        return user
    
    def get_guide_menu_item(self, request):
        """
        Helper method to find the wagtail guide MenuItem in the appropriate menu.
        
        In Wagtail 6.x, we need to provide a request to get menu items visible for that request.
        This checks admin_menu as help_menu will not be used.
        
        Args:
            request: The HTTP request object
            
        Returns:
            MenuItem or None: The guide menu item if found
        """
        guide_url = reverse('wagtaileditorguide')
        
                
        admin_menu_items = admin_menu.menu_items_for_request(request)
        for item in admin_menu_items:
            print( item.url)
            if isinstance(item, MenuItem) and item.url == guide_url:
                return item
                
        return None
    
    @override_settings(
       
        FLAGS={
            'ROPON.ENABLE_WAGTAIL_GUIDE': [('boolean', False)],
        }
    )
    def test_guide_not_accessible_when_feature_flag_disabled(self):
        """
        Test that the Wagtail guide is not accessible when the feature flag is disabled.
        Verifies menu item absence and inaccessible guide URL for a Moderator user.
        """

        

        # Login as moderator instead of admin/superuser
        self.client.force_login(self.moderator_user)
        
        # Request the admin page
        response = self.client.get(self.admin_home_url)
        self.assertEqual(response.status_code, 200, "Admin page should be accessible to Moderator")
        
        # Check that the guide label is not in the response content
        self.assertNotContains(response, wagtail_guide_settings.WAGTAIL_GUIDE_MENU_LABEL, msg_prefix="Menu label should not be present for Moderator when flag is disabled")
        
        # Check if guide MenuItem is not in the menu registry
        menu_item = self.get_guide_menu_item(response.wsgi_request)
        self.assertIsNone(menu_item, "Guide MenuItem should not be in the menu for Moderator when flag is disabled")
        
  
    @override_settings(
       
        FLAGS={
            'ROPON.ENABLE_WAGTAIL_GUIDE': [('boolean', True)],
        }
    )
    def test_guide_accessible_when_feature_flag_enabled(self):
        """
        Test that the Wagtail guide is accessible when the feature flag is enabled.
        Verifies menu item presence, label content, and URL accessibility for a Moderator user.
        """
        # Login as moderator instead of admin/superuser
        self.client.force_login(self.moderator_user)
        
        # Request the admin page and verify success
        response = self.client.get(self.admin_home_url)
        self.assertEqual(response.status_code, 200, "Admin page should be accessible to Moderator")
        
        # Test that guide URL is accessible to Moderator
        guide_response = self.client.get(self.guide_url)
        self.assertEqual(guide_response.status_code, 200, "Guide page should be accessible to Moderator when flag is enabled")
        
        # Check for the menu label in the response content
        self.assertContains(response, wagtail_guide_settings.WAGTAIL_GUIDE_MENU_LABEL , msg_prefix="Menu label should be present for Moderator")
        
        # Verify MenuItem is registered with the correct label
        menu_item = self.get_guide_menu_item(response.wsgi_request)
        self.assertIsNotNone(menu_item, "Guide MenuItem should be in menu for Moderator")
        self.assertEqual(menu_item.label, wagtail_guide_settings.WAGTAIL_GUIDE_MENU_LABEL , "Menu item should have the correct label")
        
        # Verify the menu item has the correct URL
        self.assertEqual(menu_item.url, self.guide_url, "Menu item should link to the correct URL")
    
     
    