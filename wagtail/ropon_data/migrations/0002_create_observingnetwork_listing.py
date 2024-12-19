from django.db import migrations
from wagtail.models import Page, GroupPagePermission
from django.contrib.auth.models import Group
from ropon_data.models import ObservingNetwork, ObservingNetworkListing
from django.contrib.auth.models import Permission


APP_LABEL = ObservingNetworkListing._meta.app_label

HOMEPAGE_SLUG = 'home'
ON_LISTING_SLUG = 'observingnetworks'


def create_on_listing(apps, schema_editor):
    """Creates the ROPON listing page if it doesn't exist."""    

    # Get the home page
    home_page = Page.objects.get(slug=HOMEPAGE_SLUG)

    # Create the ObservingNetworkListing page as a child of the home page
    if not ObservingNetworkListing.objects.filter(slug=ON_LISTING_SLUG).exists():
        observingnetwork_listing = ObservingNetworkListing(
            title='Observing Networks',
            slug=ON_LISTING_SLUG,
        )
        home_page.add_child(instance=observingnetwork_listing)
        
        # Stop inheriting permissions from the parent page
        observingnetwork_listing.permissions_inheritance_from = None
        observingnetwork_listing.save()

        observingnetwork_listing.save_revision().publish()

    
    # Remove all group permissions for observingnetwork_listing page
    GroupPagePermission.objects.filter(page=observingnetwork_listing).delete()

    # Fetch the groups
    editors_group = Group.objects.get(name='Editors')
    moderators_group = Group.objects.get(name='Moderators')

    # Remove access to Root page for Editors and Moderators
    
    root_page = Page.objects.get(depth=1)
    GroupPagePermission.objects.filter(
        page=root_page,
        group__in=[editors_group, moderators_group]
    ).delete()

    # Assign permissions to ObservingNetworkListing for Editors
    # Editors should have 'add' permission

    
    
    GroupPagePermission.objects.create(
        group=editors_group,
        page=observingnetwork_listing,
        permission_type='add',
    )

    # Assign permissions to ObservingNetworkListing for Moderators
    # Moderators should have 'add', 'edit', 'lock', 'publish', and 'unlock' permissions
    
    permission_types = ['add', 'change', 'lock', 'publish', 'unlock']
    #TODO: Permission_types is depcrecated, use the actual permission names
    
    for permission_type in permission_types:
        print(f" Adding permission {permission_type} to Moderators group")
        try:
            GroupPagePermission.objects.create(
                group=moderators_group,
                page=observingnetwork_listing,
                permission_type=permission_type,
            )
        except Permission.DoesNotExist:
            print(f"Permission {permission_type} does not exist")
    

def remove_on_listing(apps, schema_editor):
    # Import models directly
    
    # Delete the ObservingNetworkListing page
    try:
        ObservingNetworkListing.objects.filter(slug = ON_LISTING_SLUG).delete()
    except ObservingNetworkListing.DoesNotExist:
        pass
    
class Migration(migrations.Migration):

    dependencies = [
        ('ropon_data', '0001_initial'),
        ('wagtailsearch', '0008_remove_query_and_querydailyhits_models'),
        ('wagtailforms', '0004_add_verbose_name_plural'),
    ]

    operations = [
        migrations.RunPython(create_on_listing, remove_on_listing),
    ]
