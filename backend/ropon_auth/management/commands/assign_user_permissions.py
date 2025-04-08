from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Management command to assign add and change permissions for the User model
    to the Moderators group.
    
    This command will check if permissions already exist before assigning new ones,
    and will only assign add and change permissions (not delete).
    """
    help = 'Assigns add and change permissions for User model to the Moderators group'

    def handle(self, *args, **options):
        logger.info("Starting to assign user permissions to Moderators group")
        
        # Get the Moderators group or log warning if it doesn't exist
        try:
            moderators = Group.objects.get(name='Moderators')
            logger.info("Found Moderators group")
        except Group.DoesNotExist:
            logger.warning("'Moderators' group does not exist. No permissions assigned.")
            return

        # Get the User model using get_user_model
        User = get_user_model()
        model_name = User._meta.model_name
        logger.info(f"Using user model: {User.__name__}")
        
        # Get content type for the User model
        content_type = ContentType.objects.get_for_model(User)
        
        # Check if group already has permissions for User model
        existing_perms = moderators.permissions.filter(content_type=content_type)
        if existing_perms.exists():
            logger.warning("Permissions for User model already exist for Moderators group. No changes made.")
            return
        
        # Get only add and change permissions for the User model
        permissions_to_add = Permission.objects.filter(
            content_type=content_type,
            codename__in=[f'add_{model_name}', f'change_{model_name}']
        )
        
        if not permissions_to_add:
            logger.warning(f"Could not find add/change permissions for {model_name}")
            return
            
        try:
            # Add the permissions to the group
            moderators.permissions.add(*permissions_to_add)
            logger.info(self.style.SUCCESS(
                f"Successfully assigned {permissions_to_add.count()} permissions for model {model_name} to Moderators group"
            ))
            
            # List the specific permissions added
            for perm in permissions_to_add:
                logger.info(f"Added permission: {perm.codename}")
                
        except Exception as e:
            logger.error(self.style.ERROR(f"Error adding permissions for model {model_name}: {e}"))