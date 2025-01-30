import datetime
from wagtail.test.utils import WagtailPageTestCase
from wagtail.blocks import StreamValue
from django.core.exceptions import ValidationError
from home.models import HomePage
from ropon_data.models import ObservingNetworkPage, ObservingNetworkIndexPage, Organization, ObservingNetworkOrganization
from wagtail.models import Page
from wagtail.test.utils.form_data import nested_form_data, streamfield

class ObservingNetworkPageTests(WagtailPageTestCase):
    def setUp(self):

        self.home_page = Page.objects.get(slug='home')
        self.index_page = ObservingNetworkIndexPage(title='Observing Networks')
        self.home_page.add_child(instance=self.index_page)
        self.index_page.save_revision().publish()


    def get_soso_geometry_field(self,valid=True):
        return  [
                ('bounding_box', {
                    'southwest': {
                        'latitude': -60.0,
                        'longitude': -180.0
                    },
                    'northeast': {
                        'latitude': 60.0,
                        'longitude': 180.0
                    }
                })
            ] if valid else [
                ('bounding_box', {
                    'southwest': {
                        'latitude': 60.0, # invalid
                        'longitude': 180.0
                    },
                    'northeast': {
                        'latitude': -60.0,
                        'longitude': -180.0
                    }
                })
            ]
        
    def to_lazy_stream_data_format(self, data):
        return [{'type': block_name, 'value': block_value} for block_name, block_value in data]

    def get_metadata_catalog_url_field(self, valid=True):
        return [
            ('url', 'http://example.com/catalog1'),
            ('url', 'http://example.com/catalog2')
        ] if valid else [
            ('url', 'invalid-url')
        ]
    def get_data_repository_url_field(self, valid=True):
        data_repository_url_data= [
            ('url', 'http://example.com/repository1'),
            ('url', 'http://example.com/repository2')
        ] if valid else [
            ('url', 'invalid-url')
        ]

        return StreamValue(
            ObservingNetworkPage.data_repository_url.field.stream_block,
            data_repository_url_data,
            is_lazy=False
        )

    def get_base_page_data(self):
        return {
            'title': 'Test Network',
            'name': 'Test Network',
            'abbreviation': 'TN',
            'description': 'A test network',
            'website_url': 'http://example.com',
            'logo_url': 'http://example.com/logo.png',
            'ropon_id': '12345',
            'contact': 'contact@example.com',
            'has_catalog': 'yes'
        }
    
    
    def get_page_data(self, valid=True, lazy_stream_data=False):
        page_data = self.get_base_page_data().copy()
        geometry_field_data = self.get_soso_geometry_field(valid)
        metadata_catalog_url_data = self.get_metadata_catalog_url_field(valid)
        
        if lazy_stream_data:
            geometry_field_data = self.to_lazy_stream_data_format(geometry_field_data)
            metadata_catalog_url_data = self.to_lazy_stream_data_format(metadata_catalog_url_data)

        page_data["geometry_field"] = StreamValue(
                ObservingNetworkPage.geometry_field.field.stream_block,
                geometry_field_data,
                is_lazy=lazy_stream_data)
        
        page_data["metadata_catalog_url"] = StreamValue(
                ObservingNetworkPage.metadata_catalog_url.field.stream_block,
                metadata_catalog_url_data,
                is_lazy=lazy_stream_data)
        
        return page_data
      
      
    def get_valid_page_data_streamfield(self):
        return nested_form_data({
            'title': 'Test Network',
            'name': 'Test Network',
            'abbreviation': 'TN',
            'description': 'A test network',
            'website_url': 'http://example.com',
            'logo_url': 'http://example.com/logo.png',
            'ropon_id': '12345',
            'contact': 'contact@example.com',
            'has_catalog': 'yes',
            'geometry_field': streamfield([
                 ('bounding_box', {
                    'southwest': {
                        'latitude': -60.0,
                        'longitude': -180.0
                    },
                    'northeast': {
                        'latitude': 60.0,
                        'longitude': 180.0
                    }
                })
            ]),
            'metadata_catalog_url': streamfield([
                ('url', 'http://example.com/catalog1'),
                ('url', 'http://example.com/catalog2')
            ])
        })
    
    def test_valid_page_creation(self):
        page = ObservingNetworkPage(**self.get_page_data())
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        self.assertTrue(ObservingNetworkPage.objects.filter(title='Test Network').exists())

    def test_valid_parent_page_types(self):
        self.assertAllowedParentPageTypes(ObservingNetworkPage, {ObservingNetworkIndexPage})

    def test_invalid_parent_page_types(self):
        with self.assertRaises(AssertionError):
            self.assertAllowedParentPageTypes(ObservingNetworkPage, {HomePage})

    def test_missing_required_fields(self):
        page_data = self.get_page_data(valid=True)
        page_data.pop('name') # remove required field
        page = ObservingNetworkPage(**page_data)
            
        with self.assertRaises(ValidationError) as cm:
        
            self.index_page.add_child(instance=page)
            page.save_revision().publish()

        self.assertIn('name', cm.exception.error_dict)

    def test_max_length_fields(self):
        page_data = self.get_page_data(valid=True)
        page_data['name'] = 'a' * 257
        page = ObservingNetworkPage(**page_data)
        
        with self.assertRaises(ValidationError) as cm:
            self.index_page.add_child(instance=page)
            page.save_revision().publish()

        self.assertIn('name', cm.exception.error_dict)
        
    def test_name_empty_string(self):
        page_data = self.get_page_data(valid=True)
        page_data['name'] = ''
        page = ObservingNetworkPage(**page_data)
        
        with self.assertRaises(ValidationError) as cm:
            self.index_page.add_child(instance=page)
            page.save_revision().publish()

        self.assertIn('name', cm.exception.error_dict)
    
    def test_start_year_in_future(self):
        page_data = self.get_page_data(valid=True)
        page_data['start_year'] = datetime.datetime.now().year + 1
        page = ObservingNetworkPage(**page_data)
        
        with self.assertRaises(ValidationError) as cm:
            self.index_page.add_child(instance=page)
            page.save_revision().publish()

        self.assertIn('start_year', cm.exception.error_dict)

    def test_ropon_id_unique(self):
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        page2 = ObservingNetworkPage(**page_data)
        with self.assertRaises(ValidationError) as cm:
            self.index_page.add_child(instance=page2)
            page2.save_revision().publish()

        self.assertIn('ropon_id', cm.exception.error_dict)

    def test_update_page(self):
        page = ObservingNetworkPage(**self.get_page_data())
        self.index_page.add_child(instance=page)
        page.save_revision().publish()

        new_page = ObservingNetworkPage.objects.get(slug=page.slug)
        
        new_page.name = 'Updated Name'
        
        new_page.save_revision().publish()
        self.assertTrue(ObservingNetworkPage.objects.filter(title='Updated Name').exists())

    def test_observing_network_api_access(self):
        organization = Organization.objects.create(name='Test Organization')
        
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        ObservingNetworkOrganization.objects.create(
            observingnetwork=page,
            organization=organization
        )
        
        saved_page = ObservingNetworkPage.objects.get(slug=page.slug)
        response = self.client.get(f'/api/v2/networks/{saved_page.id}/')
        response_data = response.json()
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['name'], 'Test Network')
        self.assertEqual(len(response_data['metadata_catalog_url']), 2)
        self.assertEqual(len(response_data['organization_name']), 1)
        self.assertEqual(response_data['organization_name'][0], 'Test Organization')

    def test_create_multiple_metadata_catalog_urls(self):
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        saved_page = ObservingNetworkPage.objects.get(slug=page.slug)
        self.assertEqual(len(saved_page.metadata_catalog_url), 2)

    def test_update_metadata_catalog_urls(self):
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        new_page = ObservingNetworkPage.objects.get(slug=page.slug)
        new_metadata_catalog_url_data = [
            ('url', 'http://example.com/catalog3'),
            ('url', 'http://example.com/catalog4')
        ]
        new_page.metadata_catalog_url = StreamValue(
            ObservingNetworkPage.metadata_catalog_url.field.stream_block,
            new_metadata_catalog_url_data,
            is_lazy=False
        )
        new_page.save_revision().publish()
        
        updated_page = ObservingNetworkPage.objects.get(slug=new_page.slug)
        self.assertEqual(len(updated_page.metadata_catalog_url), 2)
        self.assertEqual(updated_page.metadata_catalog_url[0].value, 'http://example.com/catalog3')
        self.assertEqual(updated_page.metadata_catalog_url[1].value, 'http://example.com/catalog4')

    def test_delete_metadata_catalog_urls(self):
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        new_page = ObservingNetworkPage.objects.get(slug=page.slug)
        new_page.metadata_catalog_url = StreamValue(
            ObservingNetworkPage.metadata_catalog_url.field.stream_block,
            [],
            is_lazy=False
        )
        new_page.save_revision().publish()
        
        updated_page = ObservingNetworkPage.objects.get(slug=new_page.slug)
        self.assertEqual(len(updated_page.metadata_catalog_url), 0)

    def test_invalid_metadata_catalog_url(self):
        page_data = self.get_page_data(valid=False)
        page = ObservingNetworkPage(**page_data)
        
        url_block = page.metadata_catalog_url[0]
      
        with self.assertRaises(ValidationError):
          url_block.block.clean(url_block)
      
    
    def test_create_multiple_data_repository_urls(self):
        page_data = self.get_page_data(valid=True)
        
        page_data["data_repository_url"] = self.get_data_repository_url_field(valid=True)

        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        saved_page = ObservingNetworkPage.objects.get(slug=page.slug)
        self.assertEqual(len(saved_page.data_repository_url), 2)

    def test_update_data_repository_urls(self):
        page_data = self.get_page_data(valid=True)
        page_data["data_repository_url"] = self.get_data_repository_url_field(valid=True)
        
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        new_page = ObservingNetworkPage.objects.get(slug=page.slug)
        new_data_repository_url_data = [
            ('url', 'http://example.com/repository3'),
            ('url', 'http://example.com/repository4')
        ]
        new_page.data_repository_url = StreamValue(
            ObservingNetworkPage.data_repository_url.field.stream_block,
            new_data_repository_url_data,
            is_lazy=False
        )
        new_page.save_revision().publish()
        
        updated_page = ObservingNetworkPage.objects.get(slug=new_page.slug)
        self.assertEqual(len(updated_page.data_repository_url), 2)
        self.assertEqual(updated_page.data_repository_url[0].value, 'http://example.com/repository3')
        self.assertEqual(updated_page.data_repository_url[1].value, 'http://example.com/repository4')

    def test_delete_data_repository_urls(self):
        page_data = self.get_page_data(valid=True)
        page_data["data_repository_url"] = self.get_data_repository_url_field(valid=True)
        
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        new_page = ObservingNetworkPage.objects.get(slug=page.slug)
        new_page.data_repository_url = StreamValue(
            ObservingNetworkPage.data_repository_url.field.stream_block,
            [],
            is_lazy=False
        )
        new_page.save_revision().publish()
        
        updated_page = ObservingNetworkPage.objects.get(slug=new_page.slug)
        self.assertEqual(len(updated_page.data_repository_url), 0)

    def test_invalid_data_repository_url(self):
        page_data = self.get_page_data(valid=True)
        page_data["data_repository_url"] = self.get_data_repository_url_field(valid=False)
        
        page = ObservingNetworkPage(**page_data)
        
        url_block = page.data_repository_url[0]
      
        with self.assertRaises(ValidationError):
          url_block.block.clean(url_block)

    def test_observing_network_api_access_with_multiple_data_repository_urls(self):
        page_data = self.get_page_data(valid=True)
        page_data["data_repository_url"] = self.get_data_repository_url_field(valid=True)
        
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        saved_page = ObservingNetworkPage.objects.get(slug=page.slug)
        response = self.client.get(f'/api/v2/networks/{saved_page.id}/')
        response_data = response.json()
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['name'], 'Test Network')
        self.assertEqual(len(response_data['data_repository_url']), 2)

    def test_network_organizations_creation(self):
        # Create organization first
        organization = Organization.objects.create(name='Test Organization')
        
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        # Add organization to network
        ObservingNetworkOrganization.objects.create(
            observingnetwork=page,
            organization=organization
        )
        
        # Test retrieval
        saved_page = ObservingNetworkPage.objects.get(slug=page.slug)
        self.assertEqual(saved_page.network_organizations.count(), 1)
        self.assertEqual(saved_page.network_organizations.first().organization.name, 'Test Organization')
