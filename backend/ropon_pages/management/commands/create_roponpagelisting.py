import logging
from django.core.management.base import BaseCommand
from wagtail.models import Page, GroupPagePermission
from django.contrib.auth.models import Group
from ropon_pages.models import RoponPageListing
from django.contrib.auth.models import Permission

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


APP_LABEL = RoponPageListing._meta.app_label

HOMEPAGE_SLUG = 'home'
ROPON_LISTING_SLUG = 'ropon-pages'


class Command(BaseCommand):
    help = 'Creates the ROPON listing page if it doesn\'t exist.'

    def handle(self, *args, **kwargs):
        logger.info('Starting the creation of RoponPageListing page.')

        # Get the home page
        try:
            home_page = Page.objects.get(slug=HOMEPAGE_SLUG)
            logger.info(f'Home page found with slug {HOMEPAGE_SLUG}.')
        except Page.DoesNotExist:
            logger.error(f'Home page with slug {HOMEPAGE_SLUG} does not exist.')
            return

        # Create the RoponPageListing page as a child of the home page
        if not RoponPageListing.objects.filter(slug=ROPON_LISTING_SLUG).exists():
            ropon_listing = RoponPageListing(
                title='RoPON Pages',
                slug=ROPON_LISTING_SLUG,
            )
            home_page.add_child(instance=ropon_listing)
            
            # Stop inheriting permissions from the parent page
            ropon_listing.permissions_inheritance_from = None
            ropon_listing.save()

            ropon_listing.save_revision().publish()
            logger.info('RoponPageListing page created and published.')
        else:
            ropon_listing = RoponPageListing.objects.get(slug=ROPON_LISTING_SLUG)
            logger.info('RoponPageListing page already exists. Exiting without changes.')
            return  # Skip the permission changes if the page already exists

        # Remove all group permissions for ropon_listing page
        GroupPagePermission.objects.filter(page=ropon_listing).delete()
        logger.info('Removed all group permissions for RoponPageListing page.')

        # Fetch the groups
        try:
            editors_group = Group.objects.get(name='Editors')
            moderators_group = Group.objects.get(name='Moderators')
            logger.info('Editors and Moderators groups found.')
        except Group.DoesNotExist as e:
            logger.error(f'Group does not exist: {e}')
            return

        # Remove access to Root page for Editors and Moderators
        try:
            root_page = Page.objects.get(depth=1)
            GroupPagePermission.objects.filter(
                page=root_page,
                group__in=[editors_group, moderators_group]
            ).delete()
            logger.info('Removed access to Root page for Editors and Moderators.')
        except Page.DoesNotExist:
            logger.error('Root page does not exist.')
            return

        # Assign permissions to RoponPageListing for Moderators
        permission_types = ['add', 'change', 'lock', 'publish', 'unlock']

        for permission_type in permission_types:
            logger.info(f'Adding permission {permission_type} to Moderators group.')
            try:
                GroupPagePermission.objects.create(
                    group=moderators_group,
                    page=ropon_listing,
                    permission_type=permission_type,
                )
                logger.info(f'Permission {permission_type} added to Moderators group.')
            except Permission.DoesNotExist:
                logger.error(f'Permission {permission_type} does not exist.')

        logger.info('Finished the creation of RoponPageListing page.')
