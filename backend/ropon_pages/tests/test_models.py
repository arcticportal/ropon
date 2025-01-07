from django.test import TestCase, Client
from wagtail.models import Page
from ropon_pages.models import RoponPage, RoponPageListing
from wagtail.blocks import StreamValue

class RoponPageTests(TestCase):

    def setUp(self):
        # Get the root page

        self.root_page = Page.objects.get(slug='home')
        self.client = Client()
        print(self.root_page)
        self.ropon_listing_page = RoponPageListing(
            title='Test Listing Page',
            slug='test-listing-page'
        )
        self.root_page.add_child(instance=self.ropon_listing_page)
        self.ropon_listing_page.save_revision().publish()


    def test_ropon_page_creation(self):
        # Create a StreamValue for the body field
        body_stream = StreamValue(
            RoponPage.body.field.stream_block,
            [
                {'type': 'heading', 'value': 'Test Heading'},
                {'type': 'paragraph', 'value': 'Test paragraph content'},
            ],
            is_lazy=True
        )

        # Create an instance of RoponPage
        page = RoponPage(
            title='Test Ropon Page',
            slug='test-ropon-page',
            body=body_stream
        )

        # Add the page as a child of root and publish
        self.root_page.add_child(instance=page)
        page.save_revision().publish()

        # Assert the page exists in the database
        self.assertTrue(RoponPage.objects.filter(slug='test-ropon-page').exists())

    def test_ropon_page_api_access(self):

       
        # Create a StreamValue for the body field
        body_stream = StreamValue(
            RoponPage.body.field.stream_block,
            [
               {'type': 'heading', 'value': 'Test Heading'},
                {'type': 'paragraph', 'value': 'Test paragraph content'},
            ],
            is_lazy=True
        )

        # Create and publish the RoponPage under the listing page
        page = RoponPage(
            title='API Test Ropon Page',
            slug='api-test-ropon-page',
            body=body_stream
        )
        self.ropon_listing_page.add_child(instance=page)
        page.save_revision().publish()

        # Assert the page exists in the database
        self.assertTrue(RoponPage.objects.filter(slug='api-test-ropon-page').exists())

       
        # Make a GET request to the Wagtail API
        response = self.client.get('/api/v2/ropon_pages/?slug=api-test-ropon-page')
       
        print(response.json())
    
        # Assert the response is successful
        self.assertEqual(response.status_code, 200)

        # Parse the JSON response
        response_data = response.json()

        # Assert the page is returned in the API response
        self.assertEqual(response_data['meta']['total_count'], 1)
        self.assertEqual(response_data['items'][0]['title'], 'API Test Ropon Page')

   