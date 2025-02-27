"""Tests for home app functionality including Wagtail admin access and site name verification."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.conf import settings
from wagtail.test.utils import WagtailTestUtils

User = get_user_model()
class WagtailAdminAccessTest(TestCase, WagtailTestUtils):
    """Test case for verifying Wagtail admin access and site name for different user roles.
    
    This test suite ensures that:
    1. Superusers can access the admin interface
    2. Users in Moderators group can access the admin interface
    3. Users in Editors group can access the admin interface
    4. The site name matches the configured WAGTAIL_SITE_NAME
    """

    def setUp(self):
        """Set up the test environment with different user types and groups."""
        # Create the superuser
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='superuser@example.com',
            password='password'
        )

        # Create regular users
        self.moderator_user = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='password'
        )
        
        self.editor_user = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='password'
        )

        # Create and assign groups
        moderators_group, _ = Group.objects.get_or_create(name='Moderators')
        editors_group, _ = Group.objects.get_or_create(name='Editors')

        self.moderator_user.groups.add(moderators_group)
        self.editor_user.groups.add(editors_group)

        # Set up the client
        # self.client = Client()
        self.login(self.superuser)

    def test_superuser_admin_access(self):
        """Test that superuser can access admin and sees correct site name."""
        print(self.superuser)
        # self.login(self.superuser)
        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, settings.WAGTAIL_SITE_NAME)

    def test_moderator_admin_access(self):
        """Test that moderator can access admin and sees correct site name."""
        self.login(self.moderator_user)
        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, settings.WAGTAIL_SITE_NAME)

    def test_editor_admin_access(self):
        """Test that editor can access admin and sees correct site name."""
        self.login(self.editor_user)
        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, settings.WAGTAIL_SITE_NAME)