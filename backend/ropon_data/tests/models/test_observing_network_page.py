import datetime
from unittest.mock import patch, Mock
import requests
from django.core.cache import cache
from django.test import override_settings
from wagtail.test.utils import WagtailPageTestCase
from wagtail.blocks import StreamValue
from django.core.exceptions import ValidationError
from home.models import HomePage
from ropon_data.models import ObservingNetworkPage, ObservingNetworkIndexPage, Organization, ObservingNetworkOrganization, User, get_observing_network_help_content
from wagtail.models import Page
from wagtail.test.utils.form_data import nested_form_data, streamfield
from uuid import UUID
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import clear_url_caches, set_urlconf

User = get_user_model()

class ObservingNetworkPageTests(WagtailPageTestCase):
    def setUp(self):
        super().setUp()
        self.ROPON_ID_FLAG = 'ROPON.DATA.ENABLE_ON_API_ROPONID_DETAILS'

        self.home_page = Page.objects.get(slug='home')
        self.index_page = ObservingNetworkIndexPage(title='Observing Networks')
        self.home_page.add_child(instance=self.index_page)
        self.index_page.save_revision().publish()

         # Create test users with different permissions
        self.superuser = self.create_superuser(
            username='superuser',
            email='super@example.com',
            password='password'
        )
        
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='password'
        )
        
        self.editor = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='password'
        )

        # Create groups and add users
        moderators_group = Group.objects.get(name='Moderators')
        editors_group = Group.objects.get(name='Editors')
        self.moderator.groups.add(moderators_group)
        self.editor.groups.add(editors_group)
        
        # Clear the cache to ensure fresh data
        cache.clear()

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
            'logo_url': 'https://polarobservingregistry.org/assets/ropon-text.png',
            # 'ropon_id': '12345',
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
            'logo_url': 'https://polarobservingregistry.org/assets/ropon-text.png',
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
            ]),
            'data_repository_url': streamfield([
                ('url', 'http://example.com/repository1'),
                ('url', 'http://example.com/repository2')
            ]),
            'domains': [1, 2],  # Assuming these are valid domain IDs
            'disciplines': [1, 2],  # Assuming these are valid discipline IDs
            'regions': [1, 2],  # Assuming these are valid region IDs
            'subregions': [1, 2],  # Assuming these are valid subregion IDs
            'asset_types': [1, 2],  # Assuming these are valid asset type IDs

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
        page_data['name'] = 'a' * 257  # Exceeds max_length for name field
        page_data.pop('logo_url')  # Remove logo_url field as it casues below error
        # most probably due to how logo_image is saved
        '''
        raise TransactionManagementError(
        django.db.transaction.TransactionManagementError: An error occurred in the current transaction. You can't execute queries until the end of the 'atomic' block.
        '''
        page = ObservingNetworkPage(**page_data)
        
        # Also verify it fails when attempting to add to the page tree
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
        
        page_data['ropon_id'] = page.ropon_id
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

    def test_status_string(self):
        """Test that status string is correctly formatted"""
        # Create a test network page
        network = ObservingNetworkPage(**self.get_page_data())
        
        self.index_page.add_child(instance=network)
        self.assertEqual(network.status(), "LIVE")

        network.unpublish()
        # Test draft status
        self.assertEqual(network.status(), "DRAFT")
        
        
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
        organization = Organization.objects.create(name='Test Organization')
        ObservingNetworkOrganization.objects.create(
            observingnetwork=page,
            organization=organization
        )
        
        # Test retrieval
        saved_page = ObservingNetworkPage.objects.get(slug=page.slug)
        self.assertEqual(saved_page.network_organizations.count(), 1)
        self.assertEqual(saved_page.network_organizations.first().organization.name, 'Test Organization')

    def test_networks_endpoint_returns_required_meta_fields(self):
        REQUIRED_META_FIELDS =["date_last_modified"]

        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()

        response = self.client.get('/api/v2/networks/')
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('items', response_data)
        self.assertGreater(len(response_data['items']), 0)
        
        for field in REQUIRED_META_FIELDS:
            self.assertIn(field, response_data['items'][0]['meta'])
        
    def test_networks_endpoint_returns_required_fields(self):
        REQUIRED_FIELDS = ["ropon_id"]
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()

        response = self.client.get('/api/v2/networks/')
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('items', response_data)
        self.assertGreater(len(response_data['items']), 0)
        
        for field in REQUIRED_FIELDS:
            self.assertIn(field, response_data['items'][0])



    def test_networks_endpoint_excludes_unnecessary_meta_fields(self):
        EXCLUDED_META_FIELDS = ['html_url', 'type']
        
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()

        response = self.client.get('/api/v2/networks/')
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('items', response_data)
        self.assertGreater(len(response_data['items']), 0)
        
        for field in EXCLUDED_META_FIELDS:
            self.assertNotIn(field, response_data['items'][0]['meta'])

    def test_network_detail_endpoint_excludes_unnecessary_fields(self):
        EXCLUDED_META_FIELDS = [
            'seo_title',
            'html_url',
            'search_description',
            'parent'
        ]

        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()

        response = self.client.get(f'/api/v2/networks/{page.id}/')
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        for field in EXCLUDED_META_FIELDS:
            self.assertNotIn(field, response_data['meta'])

    def test_api_access_by_pk(self):
        """Test that the API endpoint can be accessed using the pk"""
        # Create test page
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        # Test access using pk
        response = self.client.get(f'/api/v2/networks/{page.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], page.name)
        self.assertEqual(response.json()['ropon_id'], str(page.ropon_id))

    
    def test_api_access_invalid_ropon_id(self):
        """Test that the API returns 404 for invalid ropon_id"""
        invalid_uuid = '12345678-1234-4321-abcd-12345678abcd'
        response = self.client.get(f'/api/v2/networks/{invalid_uuid}/')
        self.assertEqual(response.status_code, 404)
 
    def test_api_access_with_invalid_pk(self):
        """Test that the API returns 404 for invalid pk"""
        invalid_pk = 99999  # Assuming this pk doesn't exist
        response = self.client.get(f'/api/v2/networks/{invalid_pk}/')
        self.assertEqual(response.status_code, 404)

    def test_api_access_malformed_uuid(self):
        """Test that malformed UUIDs return appropriate error"""
        malformed_uuid = '12345-not-a-uuid'
        response = self.client.get(f'/api/v2/networks/{malformed_uuid}/')
        self.assertEqual(response.status_code, 404)

    def test_api_access_non_existent_ropon_id(self):
        """Test accessing with a valid UUID format but non-existent ropon_id"""
        non_existent_uuid = 'a8098c1a-f86e-11da-bd1a-00112444be1e'
        response = self.client.get(f'/api/v2/networks/{non_existent_uuid}/')
        self.assertEqual(response.status_code, 404)

    def test_api_access_draft_page_by_ropon_id(self):
        """Test that draft pages are not accessible via ropon_id"""
        # Create unpublished page
        page_data = self.get_page_data(valid=True)
        # ropon_id = UUID('12345678-1234-4321-abcd-12345678abcd')
        # page_data['ropon_id'] = ropon_id
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        # Don't publish the page
        page.unpublish()
        
        # Retrieve the generated ropon_id
        saved_page = ObservingNetworkPage.objects.get(pk=page.pk)
        ropon_id = saved_page.ropon_id
        

        response = self.client.get(f'/api/v2/networks/{ropon_id}/')
        self.assertEqual(response.status_code, 404)

        
    def test_api_response_structure_consistency(self):
        page_data = self.get_page_data(valid=True)
       
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        # Retrieve the generated ropon_id
        saved_page = ObservingNetworkPage.objects.get(pk=page.pk)
        
        # Add organization to network
        # Create organization and add to network
        organization = Organization.objects.create(name='Test Organization')
        ObservingNetworkOrganization.objects.create(
            observingnetwork=saved_page,
            organization=organization
        )

        # Get responses using both methods
        response_by_pk = self.client.get(f'/api/v2/networks/{page.pk}/')
       
        
        pk_data = response_by_pk.json()
       
        
        # Test specific field values
        fields_to_check = [
            'name', 'abbreviation', 'description', 'website_url', 
            'logo_url', 'ropon_id', 'organization_name'
        ]
       
        # Test field types
        self.assertIsInstance(pk_data['ropon_id'], str)
        self.assertIsInstance(pk_data['name'], str)
        self.assertIsInstance(pk_data['meta'], dict)
        self.assertIsInstance(pk_data['geometry_field'], list)
        self.assertIsInstance(pk_data['organization_name'], list)

        # Verify UUID format
        try:
            UUID(pk_data['ropon_id'])
        except ValueError:
            self.fail("ropon_id in response is not a valid UUID format")

    def test_api_response_meta_fields(self):
        """Test that meta fields are correctly included regardless of lookup method"""
        # Create initial page with valid data
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        # Retrieve the generated ropon_id
        saved_page = ObservingNetworkPage.objects.get(pk=page.pk)
        
        # Create test organization
        organization = Organization.objects.create(name='Test Organization')
        ObservingNetworkOrganization.objects.create(
            observingnetwork=saved_page,
            organization=organization
        )

        # Test both lookup methods with fields parameter
        required_fields = {'meta', 'name', 'ropon_id', 'organization_name'}

        fields_param = 'fields=name,ropon_id,organization_name'
        
        # Get responses using both lookup methods
        response_by_pk = self.client.get(f'/api/v2/networks/{page.pk}/?{fields_param}')
     
        # Verify both responses have exactly the same structure and content
        pk_data = response_by_pk.json()
        
        # Verify response status codes and data structure
        self.assertEqual(response_by_pk.status_code, 200)
        self.assertTrue(required_fields.issubset(set(pk_data.keys())))
     
    @override_settings(FLAGS= {'ROPON.DATA.ENABLE_ON_API_ROPONID_DETAILS': [{'condition': 'boolean','value':True}]})
    def test_api_detail_view_roponid_flag_enabled(self):
        """Test that the detail_view uses the ropon_id from kwargs when the feature flag is enabled"""
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        response = self.client.get(f'/api/v2/networks/{page.ropon_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['ropon_id'], str(page.ropon_id))

    def test_api_detail_view_roponid_flag_disabled(self):
        """Test that the detail_view uses the default primary key from kwargs when the feature flag is disabled"""
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()

        # Test with feature flag disabled (default setting)
        with self.settings(FLAGS={self.ROPON_ID_FLAG: [{'condition': 'boolean','value':False}]}):
            response = self.client.get(f'/api/v2/networks/{page.ropon_id}/')
            self.assertEqual(response.status_code, 404) # Access should fail when flag is disabled


    @override_settings(FLAGS= {'ROPON.DATA.ENABLE_ON_API_ROPONID_DETAILS': [{'condition': 'boolean','value':True}]})
    def test_api_access_both_lookup_methods_same_response(self):
        """Test that both lookup methods return the same response data"""
        page_data = self.get_page_data(valid=True)
       
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        # Retrieve the generated ropon_id
        saved_page = ObservingNetworkPage.objects.get(pk=page.pk)
        ropon_id = saved_page.ropon_id
        
        # Get responses using both methods
        response_by_pk = self.client.get(f'/api/v2/networks/{page.pk}/')
        response_by_ropon_id = self.client.get(f'/api/v2/networks/{ropon_id}/')
        response_by_pk = self.client.get(f'/api/v2/networks/{page.pk}/')
        response_by_ropon_id = self.client.get(f'/api/v2/networks/{ropon_id}/')
        
        # Compare responses
        self.assertEqual(response_by_pk.status_code, 200)
        self.assertEqual(response_by_ropon_id.status_code, 200)
        self.assertEqual(response_by_pk.json(), response_by_ropon_id.json())

    @override_settings(FLAGS= {'ROPON.DATA.ENABLE_ON_API_ROPONID_DETAILS': [{'condition': 'boolean','value':True}]})
    def test_api_access_case_sensitivity_ropon_id(self):
        """Test that UUID lookup is case-insensitive"""
        # Create test page
        page_data = self.get_page_data(valid=True)
        page = ObservingNetworkPage(**page_data)
        self.index_page.add_child(instance=page)
        page.save_revision().publish()

        # Retrieve the generated ropon_id
        saved_page = ObservingNetworkPage.objects.get(pk=page.pk)
        ropon_id = saved_page.ropon_id
        
        # Test with lowercase UUID
        lowercase_uuid = str(ropon_id).lower()
        response = self.client.get(f'/api/v2/networks/{lowercase_uuid}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['ropon_id'], str(ropon_id))

        # Test with uppercase UUID
        uppercase_uuid = str(ropon_id).upper()
        response = self.client.get(f'/api/v2/networks/{uppercase_uuid}/')
        self.assertEqual(response.status_code, 404)

    @override_settings(FLAGS= {'ROPON.BASE.USE_CUSTOM_PAGE_CREATE_EDIT_VIEWS': [{'condition': 'boolean','value':True}]})
    def test_missing_required_fields_validation_message(self):
        """Test that correct validation message is shown when required fields are missing"""
        # Get valid page data and remove a required field
        try:
            # First clear URL caches and reload URLs with the flag enabled
            clear_url_caches()
            import sys
            if 'ropon.urls' in sys.modules:
                reload = __import__('importlib').reload
                reload(sys.modules['ropon.urls'])
            set_urlconf('ropon.urls')
            
            # Ensure the custom create/edit views are enabled
            page_data = self.get_valid_page_data_streamfield()
            page_data.pop('name')  # Remove required field

            # Login as editor to access the create view
            self.login(self.editor)
            
            # Attempt to create the page via POST request
            response = self.client.post(
                f'/admin/pages/add/ropon_data/observingnetworkpage/{self.index_page.id}/',
                page_data
            )

            # Check response
            self.assertEqual(response.status_code, 200)  # Form should return with errors
            self.assertContains(
                response,
                "Ensure all fields marked with an asterisk (*) are completed."
            )
        finally:
            # Reset URL configuration
            clear_url_caches()
            set_urlconf(None)

    def test_help_panel_template_functionality(self):
        """Test that the help panel template is rendered correctly and contains expected content"""
        # Test that the helper function can render the template correctly
        help_content = get_observing_network_help_content()
        
        # Check that content is not empty
        self.assertIsNotNone(help_content)
        self.assertNotEqual(help_content.strip(), '')
        
        # Check that the content contains expected elements from the template
        self.assertIn('Here you can create and manage information for a network\'s landing page', help_content)
        self.assertIn('<b>observing network</b> – a system or organization that coordinates', help_content)
        self.assertIn('<b>discovery portal</b> for observing assets', help_content)
        self.assertIn('Tips and Tricks:', help_content)
        self.assertIn('FAQ page', help_content)
        
        # Check that template variables are properly resolved
        self.assertIn('/faq', help_content)

    @override_settings(FRONTEND_URL='https://example.com')
    def test_help_panel_template_with_custom_frontend_url(self):
        """Test that the help panel template uses the correct FRONTEND_URL setting"""
        help_content = get_observing_network_help_content()
        # Check that the custom frontend URL is used
        self.assertIn('https://example.com/ropon-pages/faq', help_content)

    def test_help_panel_template_fallback_url(self):
        """Test that the help panel template falls back to default URL when FRONTEND_URL is not set"""
        from django.conf import settings
        original_frontend_url = getattr(settings, 'FRONTEND_URL', None)
        
        try:
            if hasattr(settings, 'FRONTEND_URL'):
                delattr(settings, 'FRONTEND_URL')
            
            help_content = get_observing_network_help_content()
            
            # Check that the fallback URL is used
            self.assertIn('/faq', help_content)
            
        finally:
            # Restore original setting
            if original_frontend_url is not None:
                settings.FRONTEND_URL = original_frontend_url

    @patch('requests.head')
    @patch('requests.get')
    def test_download_logo_image_timeout_error(self, mock_get, mock_head):
        """Test that timeout errors raise ValidationError during clean()"""
        # Mock timeout error for HEAD request
        mock_head.side_effect = requests.exceptions.ConnectTimeout(
            "Connection to example.com timed out. (connect timeout=5)"
        )
        
        # Create a test page
        page_data = self.get_page_data()
        page_data['logo_url'] = 'https://example.com/logo.png'
        
        page = ObservingNetworkPage(**page_data)
        page.owner = self.superuser
        
        # This should raise ValidationError during clean()
        with self.assertRaises(ValidationError) as context:
            page.clean()
        
        # Check that the error message contains expected information
        self.assertIn('logo_url', context.exception.error_dict)
        error_messages = context.exception.error_dict['logo_url']
        # error_messages is a list, so we need to get the first error message
        error_message = str(error_messages[0])
        self.assertIn('Logo download timed out from https://example.com/logo.png', error_message)
        self.assertIn('Please check the URL or try again later', error_message)

    @patch('requests.head')
    @patch('requests.get')
    def test_download_logo_image_connection_error(self, mock_get, mock_head):
        """Test that connection errors raise ValidationError during clean()"""
        # Mock connection error for HEAD request
        mock_head.side_effect = requests.exceptions.ConnectionError(
            "HTTPSConnectionPool(host='saon.com', port=443): Max retries exceeded"
        )
        
        # Create a test page
        page_data = self.get_page_data()
        page_data['logo_url'] = 'https://saon.com/logo.png'
        
        page = ObservingNetworkPage(**page_data)
        page.owner = self.superuser
        
        # This should raise ValidationError during clean()
        with self.assertRaises(ValidationError) as context:
            page.clean()
        
        # Check that the error message contains expected information
        self.assertIn('logo_url', context.exception.error_dict)
        error_messages = context.exception.error_dict['logo_url']
        # error_messages is a list, so we need to get the first error message
        error_message = str(error_messages[0])
        self.assertIn('Unable to connect to https://saon.com/logo.png', error_message)
        self.assertIn('Please verify the URL is correct and accessible', error_message)

    @patch('requests.head')
    @patch('requests.get')
    def test_download_logo_image_http_error(self, mock_get, mock_head):
        """Test that HTTP errors (404, 500, etc.) raise ValidationError during clean()"""
        # Create a mock response object
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        
        # Create HTTPError with proper response attribute
        http_error = requests.exceptions.HTTPError("404 Not Found")
        http_error.response = mock_response
        
        # Mock HTTP error for HEAD request
        mock_head.side_effect = http_error
        
        # Create a test page
        page_data = self.get_page_data()
        page_data['logo_url'] = 'https://example.com/nonexistent-logo.png'
        
        page = ObservingNetworkPage(**page_data)
        page.owner = self.superuser
        
        # This should raise ValidationError during clean()
        with self.assertRaises(ValidationError) as context:
            page.clean()
        
        # Check that the error message contains expected information
        self.assertIn('logo_url', context.exception.error_dict)
        error_messages = context.exception.error_dict['logo_url']
        # error_messages is a list, so we need to get the first error message
        error_message = str(error_messages[0])
        self.assertIn('HTTP error accessing image: https://example.com/nonexistent-logo.png', error_message)
        self.assertIn('404', error_message)
        self.assertIn('Not Found', error_message)

    @patch('requests.head')
    def test_download_logo_image_unexpected_error(self, mock_head):
        """Test that unexpected errors raise ValidationError during clean()"""
        # Mock unexpected error
        mock_head.side_effect = Exception("Unexpected error occurred")
        
        # Create a test page
        page_data = self.get_page_data()
        page_data['logo_url'] = 'https://example.com/logo.png'
        
        page = ObservingNetworkPage(**page_data)
        page.owner = self.superuser
        
        # This should raise ValidationError during clean()
        with self.assertRaises(ValidationError) as context:
            page.clean()
        
        # Check that the error message contains expected information
        self.assertIn('logo_url', context.exception.error_dict)
        error_messages = context.exception.error_dict['logo_url']
        # error_messages is a list, so we need to get the first error message
        error_message = str(error_messages[0])
        self.assertIn('Unexpected error while validating image:', error_message)
        self.assertIn('Unexpected error occurred', error_message)

    def test_download_logo_image_no_url(self):
        """Test that no validation occurs when logo_url is empty"""
        # Create a test page without logo_url
        page_data = self.get_page_data()
        page_data['logo_url'] = ''
        
        page = ObservingNetworkPage(**page_data)
        page.owner = self.superuser
        
        # This should not raise any exception and should do nothing
        try:
            page.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError when logo_url is empty!")

    @patch('requests.head')
    def test_download_logo_image_field_not_changed(self, mock_head):
        """Test that no validation occurs when logo_url field hasn't changed"""
        # Create a test page
        page_data = self.get_page_data()
        page_data['logo_url'] = 'https://example.com/logo.png'
        
        page = ObservingNetworkPage(**page_data)
        page.owner = self.superuser
        
        # Mock that field hasn't changed and logo exists
        with patch.object(page, '_should_validate_logo_url', return_value=False):
            # This should not call requests.head since validation is skipped
            page.clean()
        
        # Verify that requests.head was not called
        mock_head.assert_not_called()
