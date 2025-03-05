from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from wagtail.test.utils import WagtailTestUtils
from ropon_data.models import (
    ObservingNetworkPage, 
    Organization,
    ObservingNetworkIndexPage,
    ObservingNetworkOrganization
)
from wagtail.models import Page


User = get_user_model()

class TestAgingNetworksReport(TestCase, WagtailTestUtils):
    """Test cases for Aging Networks report"""

    ROPON_AGING_REPORTS_FLAG = 'ROPON.REPORTS.AGING_OBSERVING_NETWORKS'

    def setUp(self):
        """Set up test data for the Aging Networks report tests"""
        # Create test users
        self.moderator_user = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='password'
        )
        # Add moderator user to existing Moderators group
        moderators_group = Group.objects.get(name='Moderators')
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

        # Create index page if it does not exist
        self.home_page = Page.objects.get(slug='home')
        self.index_page = ObservingNetworkIndexPage(title='Observing Networks')
        self.home_page.add_child(instance=self.index_page)
        self.index_page.save_revision().publish()
 
        self.page = ObservingNetworkPage(
            title='Test Network',
            name='Test Network',
            abbreviation='TN',
            description='Test Description',
            website_url='http://example.com',
            logo_url='https://polarobservingregistry.org/assets/ropon-text.png',
            owner=self.owner,
            contact='test@example.com',
            has_catalog='yes'
        )
        self.index_page.add_child(instance=self.page)
        self.page.save_revision().publish()
        # Login
        self.login(self.moderator_user)

    def test_aging_networks_view(self):
        """Test that the aging networks report view works for moderators"""
        with self.settings(FLAGS={self.ROPON_AGING_REPORTS_FLAG: [('boolean', True)]}):
            response = self.client.get(reverse('aging_networks'))
            self.assertEqual(response.status_code, 200)
            # Check that both templates are included in the response
            # self.assertTemplateUsed(response, 'wagtailadmin/reports/aging_networks.html')
            self.assertTemplateUsed(response, 'wagtailadmin/reports/aging_networks_results.html')


    def test_aging_networks_feature_flag(self):
        """Test that the report is only accessible when feature flag is enabled"""
        response = self.client.get(reverse('aging_networks'))
        self.assertEqual(response.status_code, 404)  # Should raise PermissionDenied

    def test_owner_filter(self):
        """Test that the owner filter works correctly"""
        with self.settings(FLAGS={self.ROPON_AGING_REPORTS_FLAG: [('boolean', True)]}):
            response = self.client.get(
                reverse('aging_networks'),
                {'owner': self.owner.id}
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Test Network')

    def test_organization_filter(self):
        """Test that the organization filter works correctly"""
        # Add organization to the network
        # self.page.network_organizations.create(organization=self.org)
        ObservingNetworkOrganization.objects.create(
            observingnetwork=self.page,
            organization=self.org
        )

        saved_page = ObservingNetworkPage.objects.get(id=self.page.id)
        self.assertEqual(saved_page.network_organizations.first().organization, self.org)


        with self.settings(FLAGS={self.ROPON_AGING_REPORTS_FLAG: [('boolean', True)]}):
            response = self.client.get(
                reverse('aging_networks'),
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
            logo_url='https://ropon.arcticportal.org/logo_CU_Boulder.png',
            owner=self.owner,
            last_published_at=timezone.now() - timedelta(days=50),
            contact='other@example.com',
            has_catalog='yes'
        )
        self.page.get_parent().add_child(instance=other_network).save_revision().publish()
        
        # Associate networks with different organizations
        ObservingNetworkOrganization.objects.create(
            observingnetwork=other_network,
            organization=other_org
        )

        ObservingNetworkOrganization.objects.create(
            observingnetwork=self.page,
            organization=self.org
        )
        
        with self.settings(FLAGS={self.ROPON_AGING_REPORTS_FLAG: [('boolean', True)]}):
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

        editor = Group.objects.get(name='Editors')
        regular_user.groups.add(editor)

        self.login(regular_user)
        
        with self.settings(FLAGS={self.ROPON_AGING_REPORTS_FLAG: [('boolean', True)]}):
            response = self.client.get(reverse('aging_networks'))
            self.assertEqual(response.status_code, 302)  # Should raise PermissionDenied

        
    
    def test_superuser_access_with_flag_disabled(self):
        """Test that superusers can access the report even when feature flag is disabled"""
        self.login(self.superuser)
        response = self.client.get(reverse('aging_networks'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailadmin/reports/aging_networks_results.html')

    def test_superuser_access_with_flag_enabled(self):
        """Test that superusers can access the report when feature flag is enabled"""
        self.login(self.superuser)
        with self.settings(FLAGS={self.ROPON_AGING_REPORTS_FLAG: [('boolean', True)]}):
            response = self.client.get(reverse('aging_networks'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'wagtailadmin/reports/aging_networks_results.html')