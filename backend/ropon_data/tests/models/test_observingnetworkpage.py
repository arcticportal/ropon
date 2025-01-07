from django.test import TestCase
from wagtail.models import Page
from ropon_data.models import ObservingNetworkPage, ObservingNetworkIndexPage, Domain, Discipline, Region, Subregion, AssetType, MetadataStandard, AccessProtocol
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class ObservingNetworkPageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.root_page = Page.objects.get(id=1)
        self.index_page = ObservingNetworkIndexPage(
            title='Observing Networks',
            intro='Introduction to Observing Networks'
        )
        self.root_page.add_child(instance=self.index_page)
        self.index_page.save_revision().publish()

    def test_valid_data(self):
        page = ObservingNetworkPage(
            title='Test Network',
            name='Test Network',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            geometry='67.6199 -42.3773 67.6199 17.1685 57.7191 17.1685 57.7191 -42.3773 67.6199 -42.3773',
            has_catalog='yes'
        )
        self.index_page.add_child(instance=page)
        page.full_clean()  # Should not raise any validation errors
        page.save_revision().publish()
        self.assertEqual(ObservingNetworkPage.objects.count(), 1)

    def test_missing_required_field(self):
        page = ObservingNetworkPage(
            title='Test Network',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com'
        )
        
        with self.assertRaises(ValidationError):
            self.index_page.add_child(instance=page)
           

    def test_max_length_exceeded(self):
        page = ObservingNetworkPage(
            title='Test Network',
            name='a' * 256,  # Exceeds max length
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            geometry='67.6199 -42.3773 67.6199 17.1685 57.7191 17.1685 57.7191 -42.3773 67.6199 -42.3773',
            has_catalog='yes'
  
        )
           
        with self.assertRaises(ValidationError):
            self.index_page.add_child(instance=page)
            
    def test_name_empty_string(self):
        page = ObservingNetworkPage(
            title='Test Network',
            name='',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            geometry='67.6199 -42.3773 67.6199 17.1685 57.7191 17.1685 57.7191 -42.3773 67.6199 -42.3773',
            has_catalog='yes'
  
        )
        
        with self.assertRaises(ValidationError):
            self.index_page.add_child(instance=page)
        
    def test_start_year_boundary_value(self):
        page = ObservingNetworkPage(
            title='Test Network',
            name='Test Network',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            start_year=0,  # Assuming 0 is a boundary value
            geometry='67.6199 -42.3773 67.6199 17.1685 57.7191 17.1685 57.7191 -42.3773 67.6199 -42.3773',
            has_catalog='yes'
        )
        self.index_page.add_child(instance=page)
        page.full_clean()  # Should not raise any validation errors
        page.save_revision().publish()

    def test_start_year_boundary_high_value(self):
        page = ObservingNetworkPage(
            title='Test Network',
            name='Test Network',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            start_year=2026,  # Assuming 0 is a boundary value
            geometry='67.6199 -42.3773 67.6199 17.1685 57.7191 17.1685 57.7191 -42.3773 67.6199 -42.3773',
            has_catalog='yes'
        )
        with self.assertRaises(ValidationError):
            self.index_page.add_child(instance=page)
        

    def test_roponid_unique_constraint(self):
        page = ObservingNetworkPage(
            title='Test Network',
            name='Test Network',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            geometry='67.6199 -42.3773 67.6199 17.1685 57.7191 17.1685 57.7191 -42.3773 67.6199 -42.3773',
            has_catalog='yes',
            
        )
        self.index_page.add_child(instance=page)
        page.full_clean()  
        page.save_revision().publish()

        with self.assertRaises(ValidationError):
            self.index_page.add_child(instance =ObservingNetworkPage(
                title='Test Network 2',
                name='Test Network 2',
                abbreviation='TN2',
                description='Another test network',
                website_url='http://example.com',
                logo_url='http://example.com/logo.png',
                ropon_id='12345',  # Duplicate ropon_id
                organization_name='Test Organization',
                contact='contact2@example.com',
                geometry='67.6199 -42.3773 67.6199 17.1685 57.7191 17.1685 57.7191 -42.3773 67.6199 -42.3773',
                has_catalog='yes',
                
            )
            )

    def test_related_model(self):
        domain = Domain.objects.create(name='Atmosphere')
        page = ObservingNetworkPage(
            title='Test Network',
            name='Test Network',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            geometry='67.6199 -42.3773 67.6199 17.1685 57.7191 17.1685 57.7191 -42.3773 67.6199 -42.3773',
            has_catalog='yes'
        )
        self.index_page.add_child(instance=page)
        page.full_clean()
        page.save_revision().publish()
        page.domains.add(domain)
        self.assertEqual(page.domains.first().name, 'Atmosphere')

    def test_deletion_behavior(self):
        page = ObservingNetworkPage(
            title='Test Network',
            name='Test Network',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            geometry='67.6199 -42.3773 67.6199 17.1685 57.7191 17.1685 57.7191 -42.3773 67.6199 -42.3773',
            has_catalog='yes',
            
        )

        self.index_page.add_child(instance=page)
        page.delete()
        self.assertEqual(ObservingNetworkPage.objects.count(), 0)

    def test_update_behavior(self):
        page = ObservingNetworkPage(
            title='Test Network',
            name='Test Network',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            geometry='67.6199 -42.3773 67.6199 17.1685 57.7191 17.1685 57.7191 -42.3773 67.6199 -42.3773',
            has_catalog='yes',
            
        )
        self.index_page.add_child(instance=page)
        page.name = 'Updated Network'
        page.save_revision().publish()
        self.assertEqual(ObservingNetworkPage.objects.get(id=page.id).name, 'Updated Network')
        self.assertEqual(ObservingNetworkPage.objects.get(id=page.id).title,'Updated Network')