"""
Tests for moderator access restrictions in RoponUserViewSet.

This module tests the user management permissions for moderators to ensure:
1. Moderators cannot create superusers
2. Moderators cannot see the is_superuser field on forms
3. Moderators cannot delete users
4. Moderators cannot see superusers in the user list
"""
from django.test import TestCase, RequestFactory, Client, override_settings
from django.contrib.auth.models import Group
from django.urls import reverse
from wagtail.test.utils import WagtailTestUtils
from django.contrib.auth import get_user_model
from ropon_auth.forms import RoponUserCreationForm, RoponUserEditForm
from ropon_auth.viewsets import RoponUserViewSet
from django.core.management import call_command

User = get_user_model()
class ModeratorUserAccessTestCase(TestCase, WagtailTestUtils):
    """Test case for moderator user access restrictions."""


    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the ModeratorUserAccessTestCase.
         set permissions for Moderators group
        """

        # Call the management command to set up permissions
        call_command('assign_user_permissions')
        
    def setUp(self):
        """
        Set up the test environment.
        
        Create superuser, moderator user, and regular user.
        Create a Moderators group.
        """
        # Create superuser


        # self.superuser = self.create_superuser(
        #     username='superuser',
        #     email='superuser@abc.com',
        #     password='password'
        #     )
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='superuser@example.com',
            password='password'
        )
        
        # Create moderator user
        # self.moderator = self.create_user(
        #     username='moderator',
        #     email='moderator@example.com',
        #     password='password',
        #     is_staff=True
        # )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='password'
        )
        
        # Create regular user
        # self.regular_user = self.create_test_user()
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regularuser@example.com',
            password='password'
        )
        
        # Create Moderators group and add moderator to it
        self.moderator_group = Group.objects.get(name='Moderators')
        self.moderator.groups.add(self.moderator_group)
        
        # Create request factory
        self.factory = RequestFactory()
        
        # Create client for logged-in tests
        self.client = Client()

    def test_ropon_user_creation_form_for_superuser(self):
        """Test that superusers can see the is_superuser field in creation form."""
        form = RoponUserCreationForm(
            request_user_is_superuser=True
        )
        self.assertIn('is_superuser', form.fields)

    def test_ropon_user_creation_form_for_moderator(self):
        """Test that moderators cannot see the is_superuser field in creation form."""
        form = RoponUserCreationForm(
            request_user_is_superuser=False
        )
        self.assertNotIn('is_superuser', form.fields)

    def test_ropon_user_edit_form_for_superuser(self):
        """Test that superusers can see the is_superuser field in edit form."""
        form = RoponUserEditForm(
            request_user_is_superuser=True,
            instance=self.regular_user
        )
        self.assertIn('is_superuser', form.fields)

    def test_ropon_user_edit_form_for_moderator(self):
        """Test that moderators cannot see the is_superuser field in edit form."""
        form = RoponUserEditForm(
            request_user_is_superuser=False,
            instance=self.regular_user
        )
        self.assertNotIn('is_superuser', form.fields)

    def test_viewset_get_form_class(self):
        """Test that the viewset returns the correct form class based on for_update parameter."""
        viewset = RoponUserViewSet()
        
        # Test for create form
        create_form = viewset.get_form_class(for_update=False)
        self.assertEqual(create_form, RoponUserCreationForm)
        
        # Test for update form
        edit_form = viewset.get_form_class(for_update=True)
        self.assertEqual(edit_form, RoponUserEditForm)

    def test_index_view_columns_for_superuser(self):
        """Test that superusers can see the is_superuser column in index view."""
        # Login as superuser
        self.login(self.superuser)
        
        # Get the users index page
        response = self.client.get(reverse('wagtailusers_users:index'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the page contains the is_superuser column header
        self.assertContains(response, 'is_superuser')

    @override_settings( # Set the flag to True
        FLAGS={'ROPON.AUTH.MODERATOR_USER_MANAGEMENT': [
            ("boolean", True)]}
        )
    def test_index_view_columns_for_moderator(self):
        """Test that moderators cannot see the is_superuser column in index view."""
        # Login as moderator
        self.login(self.moderator)
        
        # Get the users index page
        response = self.client.get(reverse('wagtailusers_users:index'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the table does not contain access level columns header
        
        # Use Wagtail test utilities to check HTML structure
        soup = self.get_soup(response.content)
        listing_table = soup.find('table', class_='listing')
        self.assertIsNotNone(listing_table, "Could not find table with class 'listing'")
        
        # Check that there is no th with class 'level' in the listing table
        level_headers = listing_table.find_all('th', class_='level')
        self.assertEqual(len(level_headers), 0, "Found th element with class 'level' which should not be visible to moderators")

    def test_index_view_queryset_for_superuser(self):
        """Test that superusers can see all users in index view."""
        # Login as superuser
        self.login(self.superuser)
        
        # Get the users index page
        response = self.client.get(reverse('wagtailusers_users:index'))
        self.assertEqual(response.status_code, 200)
        
        # Use Wagtail test utils to check HTML structure
        soup = self.get_soup(response.content)
        
        # Find the users listing table
        listing_table = soup.find('table', class_='listing')
        self.assertIsNotNone(listing_table, "Could not find table with class 'listing'")
        
        # Get all usernames from the table
        username_cells = listing_table.find_all('td', class_='username')
        usernames = [cell.get_text(strip=True) for cell in username_cells]
        
        # Check that all users are visible to superuser
        self.assertIn(self.superuser.username, usernames, "Superuser should be visible in the table")
        self.assertIn(self.moderator.username, usernames, "Moderator should be visible in the table")
        self.assertIn(self.regular_user.username, usernames, "Regular user should be visible in the table")

        
    @override_settings( # Set the flag to True
        FLAGS={'ROPON.AUTH.MODERATOR_USER_MANAGEMENT': [
            ("boolean", True)]}
        )   
    def test_integrated_moderator_user_management(self):
        """Integration test for moderator user management."""
        # Login as moderator
        self.login(self.moderator)
        
        # Check that moderator can see user listing but not superusers
        # Get the users index page
        response = self.client.get(reverse('wagtailusers_users:index'))
        self.assertEqual(response.status_code, 200)
        
        # Use Wagtail test utils to check HTML structure
        soup = self.get_soup(response.content)
        
        # Find the users listing table
        listing_table = soup.find('table', class_='listing')
        self.assertIsNotNone(listing_table, "Could not find table with class 'listing'")
        
        # Get all usernames from the table
        username_cells = listing_table.find_all('td', class_='username')
        usernames = [cell.get_text(strip=True) for cell in username_cells]
        
        # Check that all but superuser are visible to moderator
        self.assertNotIn(self.superuser.username, usernames, "Superuser should be visible in the table")
        self.assertIn(self.moderator.username, usernames, "Moderator should be visible in the table")
        self.assertIn(self.regular_user.username, usernames, "Regular user should be visible in the table")

        # Check create user form does not contain is_superuser field
        response = self.client.get(reverse('wagtailusers_users:add'))
        self.assertEqual(response.status_code, 200)
        # Use Wagtail test utils to check HTML structure
        soup = self.get_soup(response.content)
           
        # Check that there's no input tag with id="id_is_superuser"
        superuser_input = soup.find('input', id='id_is_superuser')
        self.assertIsNone(superuser_input, "Found input with id='id_is_superuser' which should not be visible to moderators")
        
        
        # Check edit user form does not contain is_superuser field
        response = self.client.get(reverse('wagtailusers_users:edit', args=[self.regular_user.pk]))
        self.assertEqual(response.status_code, 200)
        # Use Wagtail test utils to check HTML structure
        soup = self.get_soup(response.content)
        # Check that there's no input tag with id="id_is_superuser"
        superuser_input = soup.find('input', id='id_is_superuser')
        self.assertIsNone(superuser_input, "Found input with id='id_is_superuser' which should not be visible to moderators")
        
        # Test that moderator cannot edit a superuser
        response = self.client.get(reverse('wagtailusers_users:edit', args=[self.superuser.pk]))
        self.assertEqual(response.status_code, 302)  # Permission denied

    @override_settings( # Set the flag to True
        FLAGS={'ROPON.AUTH.MODERATOR_USER_MANAGEMENT': [
            ("boolean", True)]}
        )
    def test_moderator_user_management_flag_enabled(self):
        """
        Test that when MODERATOR_USER_MANAGEMENT flag is enabled,
        moderators can see the user management in the settings menu.
        """
        # Login as moderator
        self.login(self.moderator)
        
        # Get the admin page
        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertEqual(response.status_code, 200)
        
        # Check that users management link appears in the response
        self.assertContains(response, reverse('wagtailusers_users:index'))
        
      
    def test_moderator_user_management_flag_disabled(self):
        """
        Test that when MODERATOR_USER_MANAGEMENT flag is disabled,
        moderators cannot see the user management in the settings menu.
        """
        # Login as moderator
        self.login(self.moderator)
        
        # Set the flag to False
        with self.settings(FLAGS={'ROPON.AUTH.MODERATOR_USER_MANAGEMENT': [
            ("boolean", False)]}):
            # Get the admin page
            response = self.client.get(reverse('wagtailadmin_home'))
            self.assertEqual(response.status_code, 200)
            
            # Check that users management link appears in the response
            self.assertNotContains(response, reverse('wagtailusers_users:index'))
        
            # Use Wagtail test utils to check HTML structure
            soup = self.get_soup(response.content)
            
            
            # Look for the users link in settings menu
            users_link = soup.find('a', href=reverse('wagtailusers_users:index'))
            self.assertIsNone(users_link, "Users link found in settings menu when MODERATOR_USER_MANAGEMENT is disabled")
