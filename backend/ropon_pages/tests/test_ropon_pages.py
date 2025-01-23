from django.test import override_settings
from wagtail.test.utils import WagtailPageTestCase
from django.core.exceptions import ValidationError
from home.models import HomePage
from wagtail.rich_text import RichText
from ropon_pages.models import RoponPage, RoponPageListing
from wagtail.models import Page
from wagtail.blocks import StreamValue


class RoponPageTests(WagtailPageTestCase):
    def setUp(self):
        self.home_page = Page.objects.get(slug='home')
        self.listing_page = RoponPageListing(title='Ropon Pages')
        self.home_page.add_child(instance=self.listing_page)
        self.listing_page.save_revision().publish()

    def get_page_body(self):
        return [
                ('heading',{
                    'heading_text':'Test Heading',
                    'heading_level':'h2'}
                ),
                ('paragraph', RichText('Test paragraph content')),
            ]

    def to_lazy_stream_data_format(self, data):
        return [{'type': block_name, 'value': block_value} for block_name, block_value in data]

    def get_valid_page_data(self,title='Test Page',lazy_stream=False):
        page_data = {
                'title': title,
        }
        
        body = self.get_page_body()

        if lazy_stream:
            body = self.to_lazy_stream_data_format(body)
        
        page_data['body'] = StreamValue(RoponPage.body.field.stream_block,
                                 body,
                                    is_lazy=lazy_stream
                )
        return page_data
    
    def test_valid_page_creation(self):
        
     
        page = RoponPage(**self.get_valid_page_data(lazy_stream=False))

        # page.body.extend(self.get_valid_page_data()['body'])
    
        self.listing_page.add_child(instance=page)
        page.save_revision().publish()
        self.assertTrue(RoponPage.objects.filter(title='Test Page').exists())

    def test_valid_parent_page_types(self):
        self.assertAllowedParentPageTypes(RoponPage, {RoponPageListing})

    def test_invalid_parent_page_types(self):
        with self.assertRaises(AssertionError):
            self.assertAllowedParentPageTypes(RoponPage, {HomePage})

    def test_empty_body(self):
        page = RoponPage(title='Empty Body Page')
        self.listing_page.add_child(instance=page)
        page.save_revision().publish()
        self.assertTrue(RoponPage.objects.filter(title='Empty Body Page').exists())

    def test_max_title_length(self):
        page = RoponPage(title='a' * 256)  # Max length exceeded
        with self.assertRaises(ValidationError):
            self.listing_page.add_child(instance=page)
            page.save_revision().publish()

    def test_duplicate_page_creation(self):
        page1 = RoponPage(**self.get_valid_page_data(title='Duplicate Test'))
        self.listing_page.add_child(instance=page1)
        page1.save_revision().publish()

        page2 = RoponPage(**self.get_valid_page_data(title='Duplicate Test'))
        self.listing_page.add_child(instance=page2)
        page2.save_revision().publish()
        
        # Should create with a suffix
        self.assertTrue(RoponPage.objects.filter(slug='duplicate-test').exists())
        self.assertTrue(RoponPage.objects.filter(slug='duplicate-test-2').exists())

    def test_update_page(self):
        page = RoponPage(**self.get_valid_page_data())
        self.listing_page.add_child(instance=page)
        page.save_revision().publish()

        updated_page = RoponPage.objects.get(id=page.id)
        updated_page.title = 'Updated Title'
        # updated_page.body.extend([
        #     ('heading', {
        #         'heading_text': 'Updated Heading', 
        #         'heading_level': 'h2'}),
        #     ('paragraph', RichText( '<p>Updated paragraph content</p>')),
            
        # ])
        updated_page.save_revision().publish()

        self.assertTrue(RoponPage.objects.filter(title='Updated Title').exists())
        

    def test_api_access(self):
        page = RoponPage(**self.get_valid_page_data(title='API Test Page')) 
        self.listing_page.add_child(instance=page)
        page.save_revision().publish()

        response = self.client.get(f'/api/v2/ropon_pages/{page.id}/')
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertEqual(response_data['title'], 'API Test Page')
        self.assertIn('body', response_data)

    def test_search_fields_title(self):
        page = RoponPage(**self.get_valid_page_data(title='Unique search title')) 
        self.listing_page.add_child(instance=page)
        page.save_revision().publish()

        search_results = Page.objects.search('Unique search title')

        self.assertEqual( search_results._do_count(), 1)


    # test for cors_allowed_origins
    @override_settings(CORS_ALLOWED_ORIGINS=['http://ropon.arcticportal.org'])
    def test_cors_allowed_origin(self):
        page = RoponPage(**self.get_valid_page_data(title='CORS Test Page')) 
        self.listing_page.add_child(instance=page)
        page.save_revision().publish()
        response = self.client.get(f'/api/v2/ropon_pages/{page.id}/', HTTP_ORIGIN='http://ropon.arcticportal.org')
        print(response.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], 'http://ropon.arcticportal.org')

    # @override_settings(CORS_ALLOWED_ORIGINS=['http://ropon.arcticportal.org'])
    # def test_cors_disallowed_origin(self):
    #     page = RoponPage(**self.get_valid_page_data(title='CORS Test Page')) 
    #     self.listing_page.add_child(instance=page)
    #     page.save_revision().publish()
    #     user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    #     response = self.client.get(f'/api/v2/ropon_pages/{page.id}/', HTTP_ORIGIN='https://notallowed.com', HTTP_USER_AGENT=user_agent)
    #     print(response.headers)
    #     print(response.request)
    #     print(response.json())
    #     self.assertEqual(response.status_code, 403)
    #     self.assertNotIn('Access-Control-Allow-Origin', response)

    @override_settings(CORS_ALLOWED_ORIGINS=['http://ropon.arcticportal.org'])
    def test_cors_allowed_methods(self):
        page = RoponPage(**self.get_valid_page_data(title='CORS Test Page')) 
        self.listing_page.add_child(instance=page)
        page.save_revision().publish()

        response = self.client.options(f'/api/v2/ropon_pages/{page.id}/', HTTP_ORIGIN='http://ropon.arcticportal.org')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], 'GET, OPTIONS')

    def test_cors_disallowed_methods(self):
        page = RoponPage(**self.get_valid_page_data(title='CORS Test Page')) 
        self.listing_page.add_child(instance=page)
        page.save_revision().publish()

        response = self.client.post(f'/api/v2/ropon_pages/{page.id}/')
        self.assertEqual(response.status_code, 405)
        self.assertNotIn('Access-Control-Allow-Methods', response)

