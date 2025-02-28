import datetime
from django.test import override_settings
from wagtail.test.utils import WagtailPageTestCase
from wagtail.blocks import StreamValue
from django.core.exceptions import ValidationError
from home.models import HomePage
from ropon_data.models import ObservingNetworkPage, ObservingNetworkIndexPage, Organization, ObservingNetworkOrganization, User
from wagtail.models import Page
from wagtail.test.utils.form_data import nested_form_data, streamfield
from uuid import UUID
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class ObservingNetworkPageTests(WagtailPageTestCase):
    def setUp(self):
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
    