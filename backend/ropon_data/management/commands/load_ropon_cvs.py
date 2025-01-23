import os
import glob
from django.core.management.base import BaseCommand
from django.core.management import call_command
from pathlib import Path
import logging
from django.apps import apps

FIXTURES_PATTERN = '*_fixtures.json'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load all fixtures in the ropon_data app'

    def handle(self, *args, **kwargs):
        app_dir = Path(__file__).resolve().parent.parent.parent   
        fixtures_dir = app_dir / 'fixtures'
        if not os.path.exists(fixtures_dir):
            self.stdout.write(self.style.ERROR('Fixtures directory not found.'))
            return
        
        # Find all files ending with *_fixtures.json
        fixture_files = glob.glob(os.path.join(fixtures_dir, FIXTURES_PATTERN))
        if not fixture_files:
            self.stdout.write(self.style.WARNING('No fixture files found.'))
            return

        n_loaded_fixtures = 0
        n_data_exists = 0
        for fixture_file in fixture_files:
            fixture_name = os.path.basename(fixture_file)
            # Remove the file extension to get the fixture name
            fixture_name = os.path.splitext(fixture_name)[0]
            
            # Check if there is existing data in the relevant table
            model_name = fixture_name.split('_')[0].capitalize()
            model = apps.get_model('ropon_data', model_name)
            if model.objects.exists():
                self.stdout.write(self.style.NOTICE(f'Data already exists in the {model_name} table. Skipping fixture: {fixture_name}'))
                n_data_exists += 1
                continue

            self.stdout.write(f'Loading fixture: {fixture_name}')
            try:
                call_command('loaddata', fixture_name)
                n_loaded_fixtures += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error loading fixture {fixture_name}: {e}'))
                continue
        
        
        if n_loaded_fixtures == len(fixture_files):
            self.stdout.write(self.style.SUCCESS('All fixtures loaded successfully.'))
        
        if n_data_exists > 0:
            self.stdout.write(self.style.NOTICE(f'{n_data_exists}/{len(fixture_files)} fixtures skipped because data already exists.'))
            self.stdout.write(self.style.NOTICE(f'{n_loaded_fixtures}/{len(fixture_files)} fixtures loaded successfully.'))

        