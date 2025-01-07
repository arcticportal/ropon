import os
import sqlite3
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.management import call_command

import logging

from ropon import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check if db is empty, if so run migrations and create superuser'

    def add_arguments(self, parser):
        # argument for creating test users
        parser.add_argument(
            '--create-test-users',
            action='store_true',
            help='Create test users for RoPON'
        )
    
    def handle(self, **options):
        logger.info('Starting init script...')
        try:
            # Create migrations
            call_command('makemigrations')
            call_command('migrate')
            
        except sqlite3.OperationalError as e:
            self.stdout.write(self.style.ERROR(f'Error connecting to database: {e}'))
            return

        except Exception as e:
            self.stdout.write(f'Error creating migrations: {e}')
            return  

        # Create Super user
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', "admin")
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'it@arcticportal.org')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')

        if username and email and password:
            # Check if username already exists
            if not User.objects.filter(username=username).exists():
                try:
                    User.objects.create_superuser(username, email, password)
                    self.stdout.write(f'Superuser {username} created with email {email} and password based on default settings.')
                except Exception as e:
                    self.stdout.write(f'Error creating superuser: {e}')
                    return
            else:
                User.objects.filter(username=username).first()
                self.stdout.write(f'Superuser {username} already exists.')
        else:
            self.stdout.write('Environment variables for superuser not set.')
            self.stdout.write("Environment variables DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD must be set.")
            self.stdout.write('Or setup SUPERUSER manually by executing "python manage.py createsuperuser" at terminal.')
            return
        
     
        # Init ropon_data application

        try:
            call_command('init_ropon_data')
            self.stdout.write(self.style.SUCCESS('ropon_data initialized successfully.'))
        except CommandError as e:
            self.stdout.write(self.style.ERROR(f'Error initializing ropon_data: {e}'))
            return

        # Init ropon_pages application
        try:
            call_command('init_ropon_pages')
            self.stdout.write(self.style.SUCCESS('ropon_pages initialized successfully.'))
        except CommandError as e:
            self.stdout.write(self.style.ERROR(f'Error initializing ropon_pages: {e}'))
            return
        
        # Create test users if the flag is set
        if options['create_test_users']:
            try:
                call_command('create_test_users')
                self.stdout.write(self.style.SUCCESS('Test users created successfully.'))
            except CommandError as e:
                self.stdout.write(self.style.ERROR(f'Error creating test users: {e}'))
                return
