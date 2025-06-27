from django.core.management import call_command
from django.test import TestCase
from io import StringIO
from ropon_data.models import Domain, Discipline, Region, Subregion, AssetType, MetadataStandard, AccessProtocol

class LoadRoponCvsTests(TestCase):
    fixtures = []

    def setUp(self):
        self.out = StringIO()
        self.err = StringIO()

    def call_command(self, *args, **kwargs):
        call_command('load_ropon_cvs', *args, stdout=self.out, stderr=self.err, **kwargs)

    def test_load_fixtures_no_existing_data(self):
        self.call_command()
        output = self.out.getvalue()
        self.assertIn('All fixtures loaded successfully.', output)

    def test_load_fixtures_with_existing_data(self):
        # Create existing data
        Domain.objects.create(name='Existing Domain')
        Discipline.objects.create(name='Existing Discipline')
        Region.objects.create(name='Existing Region')
        Subregion.objects.create(name='Existing Subregion')
        AssetType.objects.create(name='Existing AssetType')
        MetadataStandard.objects.create(name='Existing MetadataStandard')
        AccessProtocol.objects.create(name='Existing AccessProtocol')

        self.call_command()
        output = self.out.getvalue()
        self.assertIn('Data already exists in the Domain table. Skipping fixture: domain_fixtures', output)
        self.assertIn('Data already exists in the Discipline table. Skipping fixture: discipline_fixtures', output)
        self.assertIn('Data already exists in the Region table. Skipping fixture: region_fixtures', output)
        self.assertIn('Data already exists in the Subregion table. Skipping fixture: subregion_fixtures', output)
        self.assertIn('Data already exists in the Assettype table. Skipping fixture: assettype_fixtures', output)
        self.assertIn('Data already exists in the Metadatastandard table. Skipping fixture: metadatastandard_fixtures', output)
        self.assertIn('Data already exists in the Accessprotocol table. Skipping fixture: accessprotocol_fixtures', output)
        self.assertNotIn('All fixtures loaded successfully.', output)
