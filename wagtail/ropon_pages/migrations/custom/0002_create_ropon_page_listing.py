from django.db import migrations
from wagtail.models import Page, GroupPagePermission
from django.contrib.auth.models import Group
from ropon_pages.models import RoponPageListing
from django.contrib.auth.models import Permission


APP_LABEL = RoponPageListing._meta.app_label

HOMEPAGE_SLUG = 'home'
ROPON_LISTING_SLUG = 'ropon-pages'


def create_ropon_page_listing(apps, schema_editor):
    """Creates the ROPON listing page if it doesn't exist."""    

    # Get the home page
    home_page = Page.objects.get(slug=HOMEPAGE_SLUG)

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

    
    # Remove all group permissions for ropon_listing page
    GroupPagePermission.objects.filter(page=ropon_listing).delete()

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
        page=ropon_listing,
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
                page=ropon_listing,
                permission_type=permission_type,
            )
        except Permission.DoesNotExist:
            print(f"Permission {permission_type} does not exist")
    

def remove_ropon_page_listing(apps, schema_editor):
    # Import models directly
    from wagtail.models import Page
    from ropon_pages.models import RoponPageListing
    
    # Delete the RoponPageListing page
    try:
        RoponPageListing.objects.filter(slug = ROPON_LISTING_SLUG).delete()
    except RoponPageListing.DoesNotExist:
        pass
    
class Migration(migrations.Migration):

    dependencies = [
        ('ropon_pages', '0001_initial'),
        ('wagtailsearch', '0008_remove_query_and_querydailyhits_models'),
        ('wagtailforms', '0004_add_verbose_name_plural'),
    ]

    operations = [
        migrations.RunPython(create_ropon_page_listing, remove_ropon_page_listing),
    ]
