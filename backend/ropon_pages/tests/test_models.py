from django.test import TestCase, Client
from wagtail.models import Page
from ropon_pages.models import RoponPage
from wagtail.blocks import StreamValue

class RoponPageTests(TestCase):

    def setUp(self):
        # Get the root page
        self.root_page = Page.objects.get(id=1)

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

    # def test_ropon_page_api_access(self):
    #     # Create a StreamValue for the body field
    #     body_stream = StreamValue(
    #         RoponPage.body.field.stream_block,
    #         [
    #            {'type': 'heading', 'value': 'Test Heading'},
    #             {'type': 'paragraph', 'value': 'Test paragraph content'},
    #         ],
    #         is_lazy=True
    #     )

    #     # Create and publish the RoponPage
    #     page = RoponPage(
    #         title='API Test Ropon Page',
    #         slug='api-test-ropon-page',
    #         body=body_stream
    #     )
    #     self.root_page.add_child(instance=page)
    #     page.save_revision().publish()


    #     # Assert the page exists in the database
    #     self.assertTrue(RoponPage.objects.filter(slug='api-test-ropon-page').exists())

    #     # Create a test client

    #     client = Client()

    #     # Make a GET request to the Wagtail API
    #     response = client.get('/api/v2/pages/?slug=api-test-ropon-page')

    #     # Assert the response is successful
    #     self.assertEqual(response.status_code, 200)

    #     # Parse the JSON response
    #     response_data = response.json()
    #     print(response_data)
    #     # Assert the page is returned in the API response
    #     self.assertEqual(response_data['meta']['total_count'], 1)
    #     self.assertEqual(response_data['items'][0]['title'], 'API Test Ropon Page')

   