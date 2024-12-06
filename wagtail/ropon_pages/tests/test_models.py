import pytest
from django.test import Client
from wagtail.models import Page
from ..models import RoponPage
from wagtail.blocks import StreamValue

# test_models.py


@pytest.mark.django_db
def test_ropon_page_creation():
    # Get the root page
    root_page = Page.objects.get(id=1)

    # Create a StreamValue for the body field
    body_stream = StreamValue(
        RoponPage.body.field.stream_block,
        [
            ('heading', 'Test Heading'),
            ('paragraph', 'Test paragraph content'),
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
    root_page.add_child(instance=page)
    page.save_revision().publish()

    # Assert the page exists in the database
    assert RoponPage.objects.filter(slug='test-ropon-page').exists()

@pytest.mark.django_db
def test_ropon_page_api_access():
    # Get the root page
    root_page = Page.objects.get(id=1)

    # Create a StreamValue for the body field
    body_stream = StreamValue(
        RoponPage.body.field.stream_block,
        [
            ('heading', 'Test Heading for API'),
            ('paragraph', 'Test paragraph content for API'),
        ],
        is_lazy=True
    )

    # Create and publish the RoponPage
    page = RoponPage(
        title='API Test Ropon Page',
        slug='api-test-ropon-page',
        body=body_stream
    )
    root_page.add_child(instance=page)
    page.save_revision().publish()

    # Create a test client
    client = Client()

    # Make a GET request to the Wagtail API
    response = client.get('/api/v2/pages/?slug=api-test-ropon-page')

    # Assert the response is successful
    assert response.status_code == 200

    # Parse the JSON response
    response_data = response.json()

    # Assert the page is returned in the API response
    assert response_data['meta']['total_count'] == 1
    assert response_data['items'][0]['title'] == 'API Test Ropon Page'