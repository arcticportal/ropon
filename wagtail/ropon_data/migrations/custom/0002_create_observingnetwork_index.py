from django.db import migrations
from wagtail.models import Page, GroupPagePermission
from django.contrib.auth.models import Group
from ropon_data.models import ObservingNetworkIndexPage
from django.contrib.auth.models import Permission


APP_LABEL = ObservingNetworkIndexPage._meta.app_label

HOMEPAGE_SLUG = 'home'
ON_INDEX_SLUG = 'observingnetworks'


def create_observingnetwork_index(apps, schema_editor):
    """Creates the ROPON Observing Network Index page if it doesn't exist."""    

    # Get the home page
    home_page = Page.objects.get(slug=HOMEPAGE_SLUG)

    # Create the Observing Networks Index page as a child of the home page
    if not ObservingNetworkIndexPage.objects.filter(slug=ON_INDEX_SLUG).exists():
        on_index = ObservingNetworkIndexPage(
            title = 'Observing Networks', 
            intro='Index page for all Observing Networks',
            slug=ON_INDEX_SLUG,
        )
        home_page.add_child(instance=on_index)
        
        # Stop inheriting permissions from the parent page
        on_index.permissions_inheritance_from = None
        on_index.save()

        on_index.save_revision().publish()

    
    # Remove all group permissions for on_index page
    GroupPagePermission.objects.filter(page=on_index).delete()

    # Fetch the groups
    editors_group = Group.objects.get(name='Editors')
    moderators_group = Group.objects.get(name='Moderators')

    # Remove access to Root page for Editors and Moderators
    
    root_page = Page.objects.get(depth=1)
    GroupPagePermission.objects.filter(
        page=root_page,
        group__in=[editors_group, moderators_group]
    ).delete()

    # Assign permissions to RoponPageListing for Editors
    # Editors should have 'add' permission

    
    
    GroupPagePermission.objects.create(
        group=editors_group,
        page=on_index,
        permission_type='add',
    )

    # Assign permissions to RoponPageListing for Moderators
    # Moderators should have 'add', 'edit', 'lock', 'publish', and 'unlock' permissions
    
    permission_types = ['add', 'change', 'lock', 'publish', 'unlock']
    #TODO: Permission_types is depcrecated, use the actual permission names
    
    for permission_type in permission_types:
        print(f" Adding permission {permission_type} to Moderators group")
        try:
            GroupPagePermission.objects.create(
                group=moderators_group,
                page=on_index,
                permission_type=permission_type,
            )
        except Permission.DoesNotExist:
            print(f"Permission {permission_type} does not exist")
    

def remove_observingnetwork_index(apps, schema_editor):
    # Import models directly
    from wagtail.models import Page
    from ropon_pages.models import RoponPageListing
    
    # Delete the RoponPageListing page
    try:
        ObservingNetworkIndexPage.objects.filter(slug = ON_INDEX_SLUG).delete()
    except ObservingNetworkIndexPage.DoesNotExist:
        pass
    
class Migration(migrations.Migration):

    dependencies = [
        ('ropon_data', '0001_initial'),
        ('wagtailsearch', '0008_remove_query_and_querydailyhits_models'),
        ('wagtailforms', '0004_add_verbose_name_plural'),
    ]

    operations = [
        migrations.RunPython(create_observingnetwork_index, remove_observingnetwork_index),
    ]
