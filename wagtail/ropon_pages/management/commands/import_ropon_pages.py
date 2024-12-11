 # management/commands/import_ropon_pages.py
import os
from django.core.management.base import BaseCommand
from ropon_pages.models import RoponPage
from django.core.management import call_command
import logging
from pathlib import Path

FILE_NAME = 'ropon_pages.json'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import Ropon pages fixtures'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='The file name for Ropon Pages fixtures'
        )

    def handle(self, **options):
        
        if RoponPage.objects.exists():
            self.stdout.write(self.style.SUCCESS('Ropon Pages already exist. Existing data will be kept.'))

            return
        
        if not options['file']:
            file_name =  FILE_NAME
        
        app_dir = Path(__file__).resolve().parent.parent.parent

        if not os.path.isabs(file_name):
            file_name = app_dir / 'fixtures' / file_name 
        if not os.path.exists(file_name):
            logging.error(f'File does not exist: {file_name}')
            return

        logging.info(f'Ropon page fixtures will be imported from : {file_name}')

        try:
            call_command('loaddata', file_name)
        except Exception as e:
            self.stdout.write(f'Error loading initial Ropon Page data: {e}')
            return

        self.stdout.write(self.style.SUCCESS('Successfully uploaded initial content for Ropon Pages.'))

        return