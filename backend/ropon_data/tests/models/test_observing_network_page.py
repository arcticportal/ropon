import datetime
from wagtail.test.utils import WagtailPageTestCase
from wagtail.blocks import StreamValue
from django.core.exceptions import ValidationError
from home.models import HomePage
from ropon_data.models import ObservingNetworkPage, ObservingNetworkIndexPage
from wagtail.models import Page
from wagtail.test.utils.form_data import nested_form_data, streamfield

class ObservingNetworkPageTests(WagtailPageTestCase):
    def setUp(self):

        self.home_page = Page.objects.get(slug='home')
        self.index_page = ObservingNetworkIndexPage(title='Observing Networks')
        self.home_page.add_child(instance=self.index_page)
        self.index_page.save_revision().publish()


    def get_bbox_geometry_field(self,valid=True):
        return [
                ('bounding_box', {
                    'south': -60.0,
                    'west': -180.0,
                    'north': 60.0,
                    'east': 180.0,
                })
            ] if valid else [
                ('bounding_box', {
                    'south': 60.0, # invalid
                    'west': 180.0,
                    'north': -60.0,
                    'east': -180.0,
                })
            ]
        
      
    def get_soso_geometry_field(self,valid=True):
        return  [
                ('soso_bounding_box', {
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
                ('soso_bounding_box', {
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

    def get_combined_geometry_field(self,valid=True):
        return self.get_soso_geometry_field(valid) + \
            self.get_bbox_geometry_field(valid)
            
    def get_base_page_data(self):
        return {
            'title': 'Test Network',
            'name': 'Test Network',
            'abbreviation': 'TN',
            'description': 'A test network',
            'website_url': 'http://example.com',
            'logo_url': 'http://example.com/logo.png',
            'ropon_id': '12345',
            'organization_name': 'Test Organization',
            'contact': 'contact@example.com',
            'has_catalog': 'yes'
        }
    
    
    def get_page_data(self,valid=True, geometry_field='combined',lazy_stream_data=False):
        page_data = self.get_base_page_data().copy()
        if geometry_field == 'combined':
            geometry_field_data = self.get_combined_geometry_field(valid)
        elif geometry_field == 'soso':
            geometry_field_data = self.get_soso_geometry_field(valid)
        elif geometry_field == 'bbox':
            geometry_field_data = self.get_bbox_geometry_field(valid)
        
        if lazy_stream_data:
            geometry_field_data = self.to_lazy_stream_data_format(geometry_field_data)

        page_data["geometry_field"] = StreamValue(
                ObservingNetworkPage.geometry_field.field.stream_block,
                geometry_field_data,
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
            'organization_name': 'Test Organization',
            'contact': 'contact@example.com',
            'has_catalog': 'yes',
            'geometry_field': streamfield([
                 ('soso_bounding_box', {
                    'southwest': {
                        'latitude': -60.0,
                        'longitude': -180.0
                    },
                    'northeast': {
                        'latitude': 60.0,
                        'longitude': 180.0
                    }
                })
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
    
    
    # def test_is_editable(self):
    #     page = ObservingNetworkPage(**self.get_valid_page_data())
    #     self.index_page.add_child(instance=page)
    #     page.save_revision().publish()
    #     self.assertPageIsEditable(page)

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
        page = ObservingNetworkPage(**self.get_page_data())
        self.index_page.add_child(instance=page)
        page.save_revision().publish()
        
        saved_page = ObservingNetworkPage.objects.get(slug=page.slug)
        response = self.client.get(f'/api/v2/networks/{saved_page.id}/')
        response_data = response.json()
        print(response_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['name'], 'Test Network')
        

        