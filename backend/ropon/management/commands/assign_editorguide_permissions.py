import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from wagtail_guide.models import EditorGuide

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Management command to assign permissions for EditorGuide settings class to the Moderators group.
    
    This command will give Moderators permission to view and edit the EditorGuide settings,
    which allows them to update the help documentation visible to editors.
    """
    help = 'Assigns EditorGuide model permissions to the Moderators group'

    def handle(self, *args, **kwargs):
        logger.info("Starting to assign EditorGuide permissions to Moderators group")
        
        try:
            # Get the Moderators group
            try:
                moderators = Group.objects.get(name='Moderators')
                logger.info("Found Moderators group")
            except Group.DoesNotExist:
                logger.error("Moderators group does not exist")
                self.stdout.write(
                    self.style.ERROR('Moderators group does not exist. Please create it first.')
                )
                return

            # Get content type for the EditorGuide model
            content_type = ContentType.objects.get_for_model(EditorGuide)
            model_name = EditorGuide._meta.model_name
            
            # Get all permissions for the model
            permissions = Permission.objects.filter(content_type=content_type)
            
            if not permissions.exists():
                logger.warning(f"No permissions found for {model_name}")
                self.stdout.write(
                    self.style.WARNING(f'No permissions found for {model_name}')
                )
                return
                
            # Check if group already has permissions
            existing_perms = moderators.permissions.filter(content_type=content_type)
            
            if existing_perms.exists():
                logger.warning("EditorGuide permissions already exist for Moderators group. No changes made.")
                self.stdout.write(
                    self.style.WARNING(
                        'EditorGuide permissions already exist for Moderators group. No changes made.'
                    )
                )
                return

            # Assign all permissions to Moderators
            try:
                moderators.permissions.add(*permissions)
                logger.info(f"Successfully assigned {permissions.count()} permissions to Moderators group")
                
                # List the specific permissions added
                for perm in permissions:
                    logger.info(f"Added permission to Moderators: {perm.codename}")
                    
            except Exception as e:
                logger.error(f"Failed to assign permissions to Moderators: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f'Failed to assign permissions to Moderators: {str(e)}')
                )
                return

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully assigned {permissions.count()} EditorGuide permissions to Moderators group'
                )
            )

        except ContentType.DoesNotExist as e:
            logger.error(f"ContentType for EditorGuide not found: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'ContentType for EditorGuide not found: {str(e)}')
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