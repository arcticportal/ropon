# wagtail/ropon_data/management/commands/load_ropon_cvs.py

import os
import glob
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Load all fixtures in the ropon_data app'

    def handle(self, *args, **kwargs):
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fixtures_dir = os.path.join(app_dir, 'fixtures')
        if not os.path.exists(fixtures_dir):
            self.stdout.write(self.style.ERROR('Fixtures directory not found.'))
            return
        
        # Find all files ending with *_fixtures.json
        fixture_files = glob.glob(os.path.join(fixtures_dir, '*_fixtures.json'))
        if not fixture_files:
            self.stdout.write(self.style.WARNING('No fixture files found.'))
            return

        for fixture_file in fixture_files:
            fixture_name = os.path.basename(fixture_file)
            # Remove the file extension to get the fixture name
            fixture_name = os.path.splitext(fixture_name)[0]
            self.stdout.write(f'Loading fixture: {fixture_name}')
            try:
                call_command('loaddata', fixture_name)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error loading fixture {fixture_name}: {e}'))
                continue

        self.stdout.write(self.style.SUCCESS('All fixtures loaded successfully.'))