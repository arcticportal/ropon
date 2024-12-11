# management/commands/export_ropon_pages.py
from django.core.management.base import BaseCommand
from django.core import serializers
from wagtail.models import Page, Revision
from ropon_pages.models import RoponPage, RoponPageListing
import json
import logging

FILE_NAME = 'ropon_pages.json'

# Configure logging
logging.basicConfig(level=logging.INFO)

class Command(BaseCommand):
    help = 'Export Ropon pages to a JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='The file to output the JSON data'
        )

    def handle(self, *args, **options):
        file_name = options['file'] if options['file'] else FILE_NAME

        if options['file']:
            try:
                with open(options['file'], 'w') as f:
                    pass
                logging.info(f'Output will be stored in : {file_name}')
            except IOError:
                logging.error(f'Cannot access file: {options["file"]}. Falling back to default file name: {FILE_NAME}')
                file_name = FILE_NAME
        else:
            logging.info(f'No file parameter provided. Using default file name: {FILE_NAME}')
        # Get the RoponPageListing
        listing_page = RoponPageListing.objects.first()
        listing_page_id = listing_page.id
        
        # Get all RoponPages
        ropon_pages = RoponPage.objects.all()
        page_ids = [p.pk for p in ropon_pages]
        
        # Update numchild for the listing page
        listing_page.numchild = len(page_ids)
        listing_page.save()
        
        data = []
        
        # 1. Export revisions
        revisions = Revision.objects.filter(
            content_type__model__in=['roponpage', 'roponpagelisting'],
            object_id__in=[listing_page_id] + page_ids
        )
        data.extend(json.loads(serializers.serialize('json', revisions)))
        
        # 2. Export listing page (parent)
        data.extend(json.loads(serializers.serialize('json', [
            Page.objects.get(id=listing_page_id)
        ])))
        
        # 3. Export RoponPageListing specific data
        data.extend(json.loads(serializers.serialize('json', [listing_page])))
        
        # 4. Export child pages
        data.extend(json.loads(serializers.serialize('json', 
            Page.objects.filter(id__in=page_ids)
        )))
        
        # 5. Export RoponPage specific data
        data.extend(json.loads(serializers.serialize('json', ropon_pages)))
        
        # Write to file
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=2)
            logging.info(f'Ropon Pages fixtures are stored in: {file_name}')
