import logging
from django.core.management.base import BaseCommand
from wagtail.models import Page, GroupPagePermission
from django.contrib.auth.models import Group
from ropon_data.models import ObservingNetworkIndexPage
from django.contrib.auth.models import Permission

APP_LABEL = ObservingNetworkIndexPage._meta.app_label

HOMEPAGE_SLUG = 'home'
ON_INDEX_SLUG = 'observingnetworks'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates the ROPON Observing Network Index page if it doesn\'t exist.'

    def handle(self, *args, **kwargs):
        logger.info('Starting the creation of the Observing Network Index page.')
        self.create_observingnetwork_index()
        logger.info('Finished the creation of the Observing Network Index page.')

    def create_observingnetwork_index(self):
        """Creates the ROPON Observing Network Index page if it doesn't exist."""

        # Get the home page
        home_page = Page.objects.get(slug=HOMEPAGE_SLUG)
        logger.info(f'Fetched home page with slug {HOMEPAGE_SLUG}.')

        # Create the Observing Networks Index page as a child of the home page
        if ObservingNetworkIndexPage.objects.filter(slug=ON_INDEX_SLUG).exists():
            logger.info(f'Observing Network Index page with slug {ON_INDEX_SLUG} already exists.')
            return
            
        on_index = ObservingNetworkIndexPage(
            title='Observing Networks',
            intro='Index page for all Observing Networks',
            slug=ON_INDEX_SLUG,
        )
        home_page.add_child(instance=on_index)
        logger.info(f'Created Observing Network Index page with slug {ON_INDEX_SLUG}.')

        # Stop inheriting permissions from the parent page
        on_index.permissions_inheritance_from = None
        on_index.save()
        logger.info('Stopped inheriting permissions from the parent page.')

        on_index.save_revision().publish()
        logger.info('Published the Observing Network Index page.')

        # Remove all group permissions for on_index page
        GroupPagePermission.objects.filter(page=on_index).delete()
        logger.info('Removed all group permissions for the Observing Network Index page.')

        # Fetch the groups
        editors_group = Group.objects.get(name='Editors')
        moderators_group = Group.objects.get(name='Moderators')
        logger.info('Fetched Editors and Moderators groups.')

        # Remove access to Root page for Editors and Moderators
        root_page = Page.objects.get(depth=1)
        GroupPagePermission.objects.filter(
            page=root_page,
            group__in=[editors_group, moderators_group]
        ).delete()
        logger.info('Removed access to Root page for Editors and Moderators.')

        # Assign permissions to Observing Network Index page for Editors
        # Editors should have 'add' permission
        GroupPagePermission.objects.create(
            group=editors_group,
            page=on_index,
            permission_type='add',
        )
        logger.info('Assigned "add" permission to Editors group for the Observing Network Index page.')

        # Assign permissions to Observing Network Index page for Moderators
        # Moderators should have 'add', 'edit', 'lock', 'publish', and 'unlock' permissions
        permission_types = ['add', 'change', 'lock', 'publish', 'unlock']

        for permission_type in permission_types:
            self.stdout.write(f"Adding permission {permission_type} to Moderators group")
            logger.info(f'Adding permission {permission_type} to Moderators group.')
            try:
                GroupPagePermission.objects.create(
                    group=moderators_group,
                    page=on_index,
                    permission_type=permission_type,
                )
                logger.info(f'Successfully added permission {permission_type} to Moderators group.')
            except Permission.DoesNotExist:
                self.stdout.write(f"Permission {permission_type} does not exist")
                logger.warning(f'Permission {permission_type} does not exist.')