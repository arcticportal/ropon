import os
import sqlite3
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from ropon_pages.models import RoponPage

import logging

from ropon import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check if db is empty, if so run migrations and create superuser'

    
    def handle(self, *args, **options):
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
                    suser = User.objects.create_superuser(username, email, password)
                    self.stdout.write(f'Superuser {username} created with email {email} and password based on default settings.')
                except Exception as e:
                    self.stdout.write(f'Error creating superuser: {e}')
                    return
            else:
                suser = User.objects.filter(username=username).first()
                self.stdout.write(f'Superuser {username} already exists.')
        else:
            self.stdout.write('Environment variables for superuser not set.')
            self.stdout.write("Environment variables DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD must be set.")
            self.stdout.write('Or setup SUPERUSER manually by executing "python manage.py createsuperuser" at terminal.')
            return
        
     
        # Load fixtures from ropon_data for controlled vocabiolaries
        try:
            call_command('load_ropon_cvs')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading fixtures: {e}'))
            return
