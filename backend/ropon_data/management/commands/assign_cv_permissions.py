from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps
import logging
from ropon_data.models import ControlledVocabularyModel

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
                app_label = model._meta.app_label
                codenames = [f'add_{model_name}', f'change_{model_name}', f'delete_{model_name}']
                
                perms = Permission.objects.filter(
                    content_type__app_label=app_label,
                    content_type__model=model_name,
                    codename__in=codenames
                )
                
                try:
                    moderators.permissions.add(*perms)
                    logger.info(f"Assigned permissions for model {model_name}")
                except Exception as e:
                    logger.error(f"Error adding permissions for model {model_name}: {e}")