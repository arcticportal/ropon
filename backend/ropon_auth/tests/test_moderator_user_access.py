"""
Tests for moderator access restrictions in RoponUserViewSet.

This module tests the user management permissions for moderators to ensure:
1. Moderators cannot create superusers
2. Moderators cannot see the is_superuser field on forms
3. Moderators cannot delete users
4. Moderators cannot see superusers in the user list
"""
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import Group
from django.urls import reverse
from wagtail.test.utils import WagtailTestUtils

from ropon_auth.models import RoponUser
from ropon_auth.forms import RoponUserCreationForm, RoponUserEditForm
from ropon_auth.viewsets import RoponUserViewSet
from ropon_auth.views import RoponUserIndexView, RoponUserCreateView, RoponUserEditView


class ModeratorUserAccessTestCase(TestCase, WagtailTestUtils):
    """Test case for moderator user access restrictions."""

    def setUp(self):
        """
        Set up the test environment.
        
        Create superuser, moderator user, and regular user.
        Create a Moderators group.
        """
        # Create superuser
        self.superuser = RoponUser.objects.create_superuser(
            username='superuser',
            email='superuser@example.com',
            password='password123'
        )
        
        # Create moderator user
        self.moderator = RoponUser.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='password123',
            is_staff=True
        )
        
        # Create regular user
        self.regular_user = RoponUser.objects.create_user(
            username='regularuser',
            email='regularuser@example.com',
            password='password123'
        )
        
        # Create Moderators group and add moderator to it
        self.moderator_group = Group.objects.create(name='Moderators')
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
        request = self.factory.get('/admin/users/')
        request.user = self.superuser
        
        view = RoponUserIndexView()
        view.request = request
        
        columns = view.columns
        column_names = [col.name for col in columns]
        self.assertIn('is_superuser', column_names)

    def test_index_view_columns_for_moderator(self):
        """Test that moderators cannot see the is_superuser column in index view."""
        request = self.factory.get('/admin/users/')
        request.user = self.moderator
        
        view = RoponUserIndexView()
        view.request = request
        
        columns = view.columns
        column_names = [col.name for col in columns]
        self.assertNotIn('is_superuser', column_names)

    def test_index_view_queryset_for_superuser(self):
        """Test that superusers can see all users in index view."""
        request = self.factory.get('/admin/users/')
        request.user = self.superuser
        
        view = RoponUserIndexView()
        view.request = request
        
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 3)  # All three users

    def test_index_view_queryset_for_moderator(self):
        """Test that moderators cannot see superusers in index view."""
        request = self.factory.get('/admin/users/')
        request.user = self.moderator
        
        view = RoponUserIndexView()
        view.request = request
        
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 2)  # Only non-superusers
        self.assertNotIn(self.superuser, queryset)

    def test_create_view_form_kwargs_for_moderator(self):
        """Test that CreateView adds request_user_is_superuser to form kwargs."""
        request = self.factory.get('/admin/users/create/')
        request.user = self.moderator
        
        view = RoponUserCreateView()
        view.request = request
        
        form_kwargs = view.get_form_kwargs()
        self.assertIn('request_user_is_superuser', form_kwargs)
        self.assertEqual(form_kwargs['request_user_is_superuser'], False)

    def test_edit_view_form_kwargs_for_moderator(self):
        """Test that EditView adds request_user_is_superuser to form kwargs."""
        request = self.factory.get(f'/admin/users/edit/{self.regular_user.pk}/')
        request.user = self.moderator
        
        view = RoponUserEditView()
        view.request = request
        view.object = self.regular_user
        
        form_kwargs = view.get_form_kwargs()
        self.assertIn('request_user_is_superuser', form_kwargs)
        self.assertEqual(form_kwargs['request_user_is_superuser'], False)
        
    def test_integrated_moderator_user_management(self):
        """Integration test for moderator user management."""
        # Login as moderator
        self.client.login(username='moderator', email='moderator@example.com', password='password123')
        
        # Check that moderator can see user listing but not superusers
        response = self.client.get(reverse('wagtailusers_users:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'regularuser')
        self.assertNotContains(response, 'superuser')
        
        # Check create user form
        response = self.client.get(reverse('wagtailusers_users:add'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id_is_superuser')
        
        # Check edit user form
        response = self.client.get(reverse('wagtailusers_users:edit', args=[self.regular_user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id_is_superuser')
        
        # Test that moderator cannot edit a superuser
        response = self.client.get(reverse('wagtailusers_users:edit', args=[self.superuser.pk]))
        self.assertEqual(response.status_code, 404)  # Should be hidden from queryset