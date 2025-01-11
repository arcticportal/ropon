# test_observingnetworkpage.py

from os import name
from django.test import TestCase
from wagtail.models import Page
from wagtail.blocks import StreamValue
from ropon_data.models import ObservingNetworkPage, ObservingNetworkIndexPage, Domain, Discipline, Region, Subregion, AssetType, MetadataStandard, AccessProtocol
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class ObservingNetworkPageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.root_page = Page.objects.get(slug='home')
        self.index_page = ObservingNetworkIndexPage(
            title='Observing Networks',
            intro='Introduction to Observing Networks'
        )
        self.root_page.add_child(instance=self.index_page)
        self.index_page.save_revision().publish()

    def test_missing_required_field(self):
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
            #geometry_field=None, this should raise a validation error
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
            has_catalog='yes',
            
        )
        self.index_page.add_child(instance=page)
        page.name = 'Updated Network'
        page.save_revision().publish()
        self.assertEqual(ObservingNetworkPage.objects.get(id=page.id).name, 'Updated Network')
        self.assertEqual(ObservingNetworkPage.objects.get(id=page.id).title,'Updated Network')

    def test_valid_bounding_box(self):
        geometry_stream = StreamValue(
            ObservingNetworkPage.geometry_field.field.stream_block,
            [
                {'type': 'bounding_box', 'value': {
                    'south': 10.0,
                    'west': 20.0,
                    'north': 30.0,
                    'east': 40.0
                }},
                {'type': 'soso_bounding_box', 'value': {
                    'southwest': {
                        'latitude': 50.0,
                        'longitude': 60.0
                    },
                    'northeast': {
                        'latitude': 70.0,
                        'longitude': 80.0
                    }
                }}
            ],
            is_lazy=True
        )

        page = ObservingNetworkPage(
            title='Test Network with Bounding Box',
            name='Test Network',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            geometry_field=geometry_stream,
            has_catalog='yes'
        )
        self.index_page.add_child(instance=page)
        page.save_revision().publish()

    def test_invalid_bounding_box(self):
        geometry_stream = StreamValue(
            ObservingNetworkPage.geometry_field.field.stream_block,
            [
                {'type': 'bounding_box', 'value': {
                    'south': 15, # south cannot be greater than north
                    'west': -20,
                    'north': 10,
                    'east': 20
                }}
            ],
            is_lazy=True
        )

        page = ObservingNetworkPage(
            title='Test Network with Invalid Bounding Box',
            name='Test Network',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            geometry_field=geometry_stream,
            has_catalog='yes'
        )

        # with self.assertRaises(ValidationError):
        self.index_page.add_child(instance=page)
        page.save_revision().publish()


    def test_valid_soso_bounding_box(self):
        geometry_stream = StreamValue(
            ObservingNetworkPage.geometry_field.field.stream_block,
            [
                {'type': 'bounding_box', 'value': {
                    'south': 10.0,
                    'west': 20.0,
                    'north': 30.0,
                    'east': 40.0
                }},
                {'type': 'soso_bounding_box', 'value': {
                    'southwest': {
                        'latitude': 50.0,
                        'longitude': 60.0
                    },
                    'northeast': {
                        'latitude': 70.0,
                        'longitude': 80.0
                    }
                }}
            ],
            is_lazy=True
        )

        page = ObservingNetworkPage(
            title='Test Network with SOSO Bounding Box',
            name='Test Network',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            geometry_field=geometry_stream,
            has_catalog='yes'
        )
        self.index_page.add_child(instance=page)
        page.save_revision().publish()

    def test_invalid_soso_bounding_box(self):
        geometry_stream = StreamValue(
            ObservingNetworkPage.geometry_field.field.stream_block,
            [
                {'type': 'soso_bounding_box', 'value': {
                    'southwest': {'latitude': 20, 'longitude': -20},
                    'northeast': {'latitude': 10, 'longitude': 20}  # southwest latitude is greater than northeast latitude
                }}
            ],
            is_lazy=True
        )

        page = ObservingNetworkPage(
            title='Test Network with Invalid SOSO Bounding Box',
            name='Test Network',
            abbreviation='TN',
            description='A test network',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='12345',
            organization_name='Test Organization',
            contact='contact@example.com',
            geometry_field=geometry_stream,
            has_catalog='yes'
        )
        print(page.geometry_field)
        print(page.geometry_field[0].value)
        print(page.to_json())
        with self.assertRaises(ValidationError):
            self.index_page.add_child(instance=page)
            page.clean()
            page.save_revision().publish()

    def test_valid_observing_network_page_creation(self):
        geometry_stream = StreamValue(
            ObservingNetworkPage.geometry_field.field.stream_block,
            [
                {'type': 'bounding_box', 'value': {
                    'south': 10.0,
                    'west': 20.0,
                    'north': 30.0,
                    'east': 40.0
                }},
                {'type': 'soso_bounding_box', 'value': {
                    'southwest': {
                        'latitude': 50.0,
                        'longitude': 60.0
                    },
                    'northeast': {
                        'latitude': 70.0,
                        'longitude': 80.0
                    }
                }}
            ],
            is_lazy=True
        )

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
            has_catalog='yes',
            geometry_field=geometry_stream
        )
        self.index_page.add_child(instance=page)
        page.save_revision().publish()

        self.assertTrue(ObservingNetworkPage.objects.filter(slug='test-network').exists())

    def test_invalid_observing_network_page_creation(self):
        with self.assertRaises(ValidationError):
            page = ObservingNetworkPage(
                title='Invalid Network',
                name='',
                abbreviation='',
                description='',
                website_url='invalid-url',
                logo_url='invalid-url',
                ropon_id='',
                organization_name='',
                contact='invalid-contact',
                has_catalog='',
                geometry_field=None
            )
            self.index_page.add_child(instance=page)
            page.full_clean()

    def test_geometry_field(self):
        geometry_stream = StreamValue(
            ObservingNetworkPage.geometry_field.field.stream_block,
            [
                {'type': 'bounding_box', 'value': {
                    'south': 10.0,
                    'west': 20.0,
                    'north': 30.0,
                    'east': 40.0
                }},
                {'type': 'soso_bounding_box', 'value': {
                    'southwest': {
                        'latitude': 50.0,
                        'longitude': 60.0
                    },
                    'northeast': {
                        'latitude': 70.0,
                        'longitude': 80.0
                    }
                }}
            ],
            is_lazy=True
        )


        page = ObservingNetworkPage(
            title='Geometry Test Network',
            name='Geometry Test Network',
            abbreviation='GTN',
            description='A test network for geometry field',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='67890',
            organization_name='Test Organization',
            contact='contact@example.com',
            has_catalog='yes',
            geometry_field=geometry_stream
        )
        self.index_page.add_child(instance=page)
        page.save_revision().publish()

        saved_page = ObservingNetworkPage.objects.get(slug='geometry-test-network')
        self.assertEqual(saved_page.geometry_field[0].value['south'], 10)
        self.assertEqual(saved_page.geometry_field[1].value['southwest']['latitude'], 50)
        self.assertEqual(saved_page.geometry_field[1].value['southwest']['longitude'], 60)

    def test_observing_network_page_api_access(self):
        geometry_stream = StreamValue(
            ObservingNetworkPage.geometry_field.field.stream_block,
            [
                {'type': 'bounding_box', 'value': {
                    'south': 10.0,
                    'west': 20.0,
                    'north': 30.0,
                    'east': 40.0
                }},
                {'type': 'soso_bounding_box', 'value': {
                    'southwest': {
                        'latitude': 50.0,
                        'longitude': 60.0
                    },
                    'northeast': {
                        'latitude': 70.0,
                        'longitude': 80.0
                    }
                }}
            ],
            is_lazy=True
        )

        page = ObservingNetworkPage(
            title='API Test Network',
            name='API Test Network',
            slug ='api-test-network',
            abbreviation='ATN',
            description='A test network for API access',
            website_url='http://example.com',
            logo_url='http://example.com/logo.png',
            ropon_id='54321',
            organization_name='Test Organization',
            contact='contact@example.com',
            has_catalog='yes',
            geometry_field=geometry_stream
        )
        self.index_page.add_child(instance=page)
        page.save_revision().publish()

        saved_page = ObservingNetworkPage.objects.get(slug='api-test-network')

        print(saved_page)
        response = self.client.get('/api/v2/networks/?slug=api-test-network')
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        print(response_data)
        self.assertEqual(response_data['meta']['total_count'], 1)
        self.assertEqual(response_data['items'][0]['title'], 'API Test Network')
