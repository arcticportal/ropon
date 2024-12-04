import pytest
from django.test import Client
from wagtail.models import Page
from wagtail.blocks import StreamValue
from ..models import RoponPage, RoponPageListing

@pytest.mark.django_db
def test_ropon_page_creation():
    # Create root page
    root_page = Page.objects.get(id=1)
    # Create RoponPageListing
    listing_page = RoponPageListing(title='Test RoponPageListing')
    root_page.add_child(instance=listing_page)
    listing_page.save_revision().publish()
    # Create body content for RoponPage
    body_content = StreamValue(
        RoponPage.body.stream_block,
        [
            ('heading', 'Test Heading'),
            ('paragraph', 'Test Paragraph'),
            ('image', None),
        ],
        is_lazy=True
    )
    # Create RoponPage
    ropon_page = RoponPage(title='Test RoponPage', body=body_content)
    listing_page.add_child(instance=ropon_page)
    ropon_page.save_revision().publish()
    # Assert that the page exists
    assert RoponPage.objects.filter(title='Test RoponPage').exists()

@pytest.mark.django_db
def test_ropon_page_api_access():
    client = Client()
    # Retrieve the first RoponPage
    ropon_page = RoponPage.objects.first()
    # Get API URL (adjust if necessary)
    response = client.get(f'/api/v2/pages/{ropon_page.id}/')
    # Assert that the response is successful
    assert response.status_code == 200
    # Check the content
    data = response.json()
    assert data['title'] == ropon_page.title