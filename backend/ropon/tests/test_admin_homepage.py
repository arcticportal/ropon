from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from wagtail.models import Site
from wagtail.test.utils import WagtailTestUtils # Import WagtailTestUtils

User = get_user_model()

class AdminHomepageSummaryPanelTests(WagtailTestUtils, TestCase): # Inherit from WagtailTestUtils
    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase
        """
        # Ensure a default Wagtail site exists.
        if not Site.objects.exists():
            # A root page is needed for Site.objects.create to work without error
            # In a real Wagtail setup, a root page would exist.
            # For testing, we might need to create a dummy one if not present.
            # However, for admin view tests, this might not be strictly necessary
            # if reverse('wagtailadmin_home') resolves correctly.
            # Let's assume the default page tree exists or is not needed for this specific view.
            Site.objects.create(hostname='localhost', port=80, is_default_site=True, root_page_id=1) # root_page_id=1 is often the default

        # Create user groups
        cls.moderators_group, _ = Group.objects.get_or_create(name='Moderators')
        cls.editors_group, _ = Group.objects.get_or_create(name='Editors')

        # Create a moderator user
        cls.moderator_user = User.objects.create_user(
            username='moderator_test_user',
            password='password',
            email='moderator@example.com',
            is_staff=True,
            is_superuser=False
        )
        cls.moderator_user.groups.add(cls.moderators_group)

        # Create an editor user
        cls.editor_user = User.objects.create_user(
            username='editor_test_user',
            password='password',
            email='editor@example.com',
            is_staff=True,
            is_superuser=False
        )
        cls.editor_user.groups.add(cls.editors_group)

    def setUp(self):
        """
        Set up for each test method.
        """
        # self.client = Client() # Client is provided by WagtailTestUtils
        self.admin_home_url = reverse('wagtailadmin_home')

    def test_admin_homepage_summary_panel_removed_for_moderator(self):
        """
        Test that the summary panel is not present on the admin homepage for moderators.
        """
        self.login(self.moderator_user) # Use self.login() from WagtailTestUtils
        response = self.client.get(self.admin_home_url)

        self.assertEqual(response.status_code, 200)
        # Check that the summary items are not in the context or are empty
        summary_items = response.context.get('summary_items')
        self.assertTrue(summary_items is None or not summary_items, "Summary items should be empty or None for moderators")

    def test_admin_homepage_summary_panel_removed_for_editor(self):
        """
        Test that the summary panel is not present on the admin homepage for editors.
        """
        self.login(self.editor_user) # Use self.login() from WagtailTestUtils
        response = self.client.get(self.admin_home_url)

        self.assertEqual(response.status_code, 200)
        # Check that the summary items are not in the context or are empty
        summary_items = response.context.get('summary_items')
        self.assertTrue(summary_items is None or not summary_items, "Summary items should be empty or None for editors")


