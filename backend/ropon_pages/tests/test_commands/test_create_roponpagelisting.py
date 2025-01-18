import logging
from django.core.management import call_command
from django.test import TestCase
from wagtail.models import Page, GroupPagePermission
from django.contrib.auth.models import Group
from ropon_pages.models import RoponPageListing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreateRoponPageListingTests(TestCase):
    def setUp(self):
        self.home_page = Page.objects.get(slug='home')
        self.editors_group = Group.objects.get(name='Editors')
        self.moderators_group = Group.objects.get(name='Moderators')
        self.slug_pagelisting = 'ropon-pages'

    def test_create_roponpagelisting(self):
        call_command('create_roponpagelisting')
        self.assertTrue(RoponPageListing.objects.filter(slug=self.slug_pagelisting).exists())
        root_page = Page.objects.get(depth=1)   
        self.assertFalse(GroupPagePermission.objects.filter(page=root_page).exists())

    def test_roponpagelisting_already_exists(self):
        ropon_listing = RoponPageListing(
            title='RoPON Pages',
            slug=self.slug_pagelisting,
        )
        self.home_page.add_child(instance=ropon_listing)
        ropon_listing.save_revision().publish()
        with self.assertLogs(level='INFO') as log:
            call_command('create_roponpagelisting')
            self.assertIn('RoponPageListing page already exists.', ".".join(log.output))
            
        self.assertTrue(RoponPageListing.objects.filter(slug=self.slug_pagelisting).exists())
        self.assertFalse(GroupPagePermission.objects.filter(page=ropon_listing).exists())
