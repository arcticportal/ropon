from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from ropon_data.models import Organization
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Management command to assign permissions for Organization model to the Moderators and Editors groups.
    
    Moderators get all permissions (add, change, delete, view).
    Editors get limited permissions (add, change) only.
    """
    help = 'Assigns Organization model permissions to Moderators and Editors groups'

    def handle(self, *args, **kwargs):
        logger.info("Starting to assign Organization permissions to groups")
        
        try:
            # Get or create the groups
            moderators, _ = Group.objects.get_or_create(name='Moderators')
            editors, _ = Group.objects.get_or_create(name='Editors')
            logger.info("Found or created Moderators and Editors groups")

            # Get content type for the model
            content_type = ContentType.objects.get_for_model(Organization)
            model_name = Organization._meta.model_name
            
            # Get all permissions for the model
            all_permissions = Permission.objects.filter(content_type=content_type)
            
            # Get only add and change permissions for Editors
            editor_permissions = Permission.objects.filter(
                content_type=content_type,
                codename__in=[f'add_{model_name}', f'change_{model_name}']
            )

            # Check if groups already have permissions
            moderator_perms = moderators.permissions.filter(content_type=content_type)
            editor_perms = editors.permissions.filter(content_type=content_type)

            if moderator_perms.exists() and editor_perms.exists():
                logger.warning("Permissions already exist for both groups. No changes made.")
                self.stdout.write(
                    self.style.WARNING(
                        'Permissions already exist for both groups. No changes made.'
                    )
                )
                return

            # Assign all permissions to Moderators
            try:
                moderators.permissions.add(*all_permissions)
                logger.info(f"Successfully assigned {all_permissions.count()} permissions to Moderators group")
                
                # List the specific permissions added for Moderators
                for perm in all_permissions:
                    logger.info(f"Added permission to Moderators: {perm.codename}")
                    
            except Exception as e:
                logger.error(f"Failed to assign permissions to Moderators: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f'Failed to assign permissions to Moderators: {str(e)}')
                )
                return

            # Assign only add and change permissions to Editors
            try:
                editors.permissions.add(*editor_permissions)
                logger.info(f"Successfully assigned {editor_permissions.count()} permissions to Editors group")
                
                # List the specific permissions added for Editors
                for perm in editor_permissions:
                    logger.info(f"Added permission to Editors: {perm.codename}")
                    
            except Exception as e:
                logger.error(f"Failed to assign permissions to Editors: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f'Failed to assign permissions to Editors: {str(e)}')
                )
                return

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully assigned {all_permissions.count()} permissions to Moderators and {editor_permissions.count()} permissions to Editors'
                )
            )

        except (Group.DoesNotExist, ContentType.DoesNotExist) as e:
            logger.error(f"Model or Group not found: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Model or Group not found: {str(e)}')
            )
        except Permission.DoesNotExist as e:
            logger.error(f"Permission not found: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Permission not found: {str(e)}')
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Unexpected error occurred: {str(e)}')
            )