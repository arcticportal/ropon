from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps
import logging
from ropon_data.models import ControlledVocabularyModel
from django.contrib.contenttypes.models import ContentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Assigns add, change, and delete permissions for all models inheriting from ControlledVocabularyModel to the Moderators group'

    def handle(self, *args, **kwargs):
        logger.info("Assigning moderator permissions")
        
        try:
            moderators = Group.objects.get(name='Moderators')
        except Group.DoesNotExist:
            logger.warning("'Moderators' group does not exist")
            return

        for model in apps.get_models():
            if model is not ControlledVocabularyModel and issubclass(model, ControlledVocabularyModel):
                model_name = model._meta.model_name
                # get content type for the model
                content_type = ContentType.objects.get_for_model(model)

                # get all permissions for the model
                permissions = Permission.objects.filter(content_type=content_type)

                # check if group already has permissions
                moderator_perms = moderators.permissions.filter(content_type=content_type)
                if moderator_perms.exists():
                    logger.warning(self.style.WARNING('Permissions already exist for Moderators group. No changes made.'))
                    return
                
                try:
                    moderators.permissions.add(*permissions)
                    logger.info(self.style.SUCCESS(f"Successfully assigned {permissions.count()} permissions for model {model_name}"))
                except Exception as e:
                    logger.error(self.style.ERROR(f"Error adding permissions for model {model_name}: {e}"))