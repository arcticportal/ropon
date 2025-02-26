from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from wagtail.test.utils import WagtailTestUtils
from ropon_data.models import ObservingNetworkPage, Organization

User = get_user_model()

class TestAgingNetworksReport(TestCase, WagtailTestUtils):
    """Test cases for Aging Networks report"""

    def setUp(self):
        # Create test users
        self.moderator_user = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='password'
        )
        moderators_group = Group.objects.create(name='Moderators')
        self.moderator_user.groups.add(moderators_group)
        
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='password'
        )

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='superuser@example.com',
            password='password'
        )

        # Create test organization
        self.org = Organization.objects.create(name='Test Organization')

        # Create test pages
        root_page = ObservingNetworkPage.objects.get(id=2)
        
        self.page = ObservingNetworkPage(
            title='Test Network',
            name='Test Network',
            abbreviation='TN',
            description='Test Description',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            owner=self.owner,
            last_published_at=timezone.now() - timedelta(days=100)
        )
        root_page.add_child(instance=self.page)
        
        # Login
        self.login(self.moderator_user)

    def test_aging_networks_view(self):
        """Test that the aging networks report view works for moderators"""
        with self.settings(FLAGS={'ROPON.REPORTS.AGING_OBSERVING_NETWORKS': [('boolean', True)]}):
            response = self.client.get(reverse('aging-networks'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'wagtailadmin/reports/aging_networks.html')

    def test_aging_networks_feature_flag(self):
        """Test that the report is only accessible when feature flag is enabled"""
        response = self.client.get(reverse('aging-networks'))
        self.assertEqual(response.status_code, 403)  # Should raise PermissionDenied

    def test_owner_filter(self):
        """Test that the owner filter works correctly"""
        with self.settings(FLAGS={'ROPON.REPORTS.AGING_OBSERVING_NETWORKS': [('boolean', True)]}):
            response = self.client.get(
                reverse('aging-networks'),
                {'owner': self.owner.id}
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Test Network')

    def test_organization_filter(self):
        """Test that the organization filter works correctly"""
        # Add organization to the network
        self.page.network_organizations.create(organization=self.org)
        
        with self.settings(FLAGS={'ROPON.REPORTS.AGING_OBSERVING_NETWORKS': [('boolean', True)]}):
            response = self.client.get(
                reverse('aging-networks'),
                {'organization': self.org.id}
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Test Network')

    def test_organization_filter_with_multiple_networks(self):
        """Test that the organization filter correctly filters networks when multiple networks and organizations exist"""
        # Create another organization and network
        other_org = Organization.objects.create(name='Other Organization')
        other_network = ObservingNetworkPage(
            title='Other Network',
            name='Other Network',
            abbreviation='ON',
            description='Other Description',
            website_url='http://other.com',
            logo_url='http://other.com/logo.png',
            owner=self.owner,
            last_published_at=timezone.now() - timedelta(days=50)
        )
        self.page.get_parent().add_child(instance=other_network)
        
        # Associate networks with different organizations
        self.page.network_organizations.create(organization=self.org)
        other_network.network_organizations.create(organization=other_org)
        
        with self.settings(FLAGS={'ROPON.REPORTS.AGING_OBSERVING_NETWORKS': [('boolean', True)]}):
            # Test filtering by first organization
            response = self.client.get(
                reverse('aging_networks'),
                {'organization': self.org.id}
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Test Network')
            self.assertNotContains(response, 'Other Network')
            
            # Test filtering by second organization
            response = self.client.get(
                reverse('aging_networks'),
                {'organization': other_org.id}
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Other Network')
            self.assertNotContains(response, 'Test Network')

    def test_non_moderator_access(self):
        """Test that non-moderators cannot access the report"""
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='password'
        )
        self.login(regular_user)
        
        with self.settings(FLAGS={'ROPON.REPORTS.AGING_OBSERVING_NETWORKS': [('boolean', True)]}):
            response = self.client.get(reverse('aging-networks'))
            self.assertEqual(response.status_code, 403)

    def test_superuser_access_with_flag_disabled(self):
        """Test that superusers can access the report even when feature flag is disabled"""
        self.login(self.superuser)
        response = self.client.get(reverse('aging-networks'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailadmin/reports/aging_networks.html')

    def test_superuser_access_with_flag_enabled(self):
        """Test that superusers can access the report when feature flag is enabled"""
        self.login(self.superuser)
        with self.settings(FLAGS={'ROPON.REPORTS.AGING_OBSERVING_NETWORKS': [('boolean', True)]}):
            response = self.client.get(reverse('aging-networks'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'wagtailadmin/reports/aging_networks.html')