import logging
from django.core.management import call_command
from django.core.management.base import BaseCommand

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize Ropon pages by calling necessary management commands.'

    def handle(self, *args, **kwargs):
        logger.info('Starting the initialization of Ropon pages.')

        try:
            logger.info('Calling create_roponpagelisting command.')
            call_command('create_roponpagelisting')
            logger.info('Successfully called create_roponpagelisting command.')
        except Exception as e:
            logger.error(f'Error occurred while calling create_roponpagelisting: {e}')
            return

        logger.info('Finished the initialization of Ropon pages.')