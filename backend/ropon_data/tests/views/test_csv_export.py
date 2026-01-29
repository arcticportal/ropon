"""
Tests for CSV export functionality of ObservingNetworkPage API.

Tests the ?format=csv query parameter support for the networks list endpoint.
"""
import csv
from io import StringIO

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from wagtail.test.utils import WagtailPageTestCase
from wagtail.models import Page

from ropon_data.models import (
    ObservingNetworkPage,
    ObservingNetworkIndexPage,
    Domain,
    Discipline,
    Region,
)
from ropon_data.blocks import SOSOBoundingBoxBlock, GeoPointBlock, NetworkIdBlock
from ropon_data.renderers import ObservingNetworkCSVRenderer


User = get_user_model()


class CSVRendererTests(TestCase):
    """Unit tests for the ObservingNetworkCSVRenderer class."""

    def test_renderer_media_type(self):
        """Test that renderer has correct media type."""
        renderer = ObservingNetworkCSVRenderer()
        self.assertEqual(renderer.media_type, 'text/csv')

    def test_renderer_format(self):
        """Test that renderer has correct format identifier."""
        renderer = ObservingNetworkCSVRenderer()
        self.assertEqual(renderer.format, 'csv')

    def test_render_empty_list(self):
        """Test rendering empty list returns headers only."""
        renderer = ObservingNetworkCSVRenderer()
        result = renderer.render([], None, None)

        # Should have headers only
        reader = csv.reader(StringIO(result))
        rows = list(reader)
        self.assertEqual(len(rows), 1)  # Headers only
        self.assertEqual(rows[0], renderer.CSV_COLUMNS)

    def test_render_none_data(self):
        """Test rendering None data returns headers only."""
        renderer = ObservingNetworkCSVRenderer()
        result = renderer.render(None, None, None)

        reader = csv.reader(StringIO(result))
        rows = list(reader)
        self.assertEqual(len(rows), 1)  # Headers only

    def test_logo_image_not_in_columns(self):
        """Test that logo_image is excluded from CSV columns (requirement #7)."""
        renderer = ObservingNetworkCSVRenderer()
        self.assertNotIn('logo_image', renderer.CSV_COLUMNS)

    def test_all_expected_columns_present(self):
        """Test that all expected columns are present in CSV."""
        renderer = ObservingNetworkCSVRenderer()
        expected_columns = [
            'name', 'abbreviation', 'ropon_id', 'description', 'website_url',
            'logo_url', 'organization_name', 'domains', 'disciplines', 'regions',
            'subregions', 'geometry_field', 'start_year', 'contact',
            'data_repository_url', 'network_id', 'asset_types', 'has_catalog',
            'metadata_access', 'machine_readable', 'metadata_standards',
            'access_protocols', 'metadata_catalog_url', 'detail_url',
            'date_last_modified',
        ]
        for col in expected_columns:
            self.assertIn(col, renderer.CSV_COLUMNS)

    def test_format_list_field(self):
        """Test that list fields are joined with comma and space."""
        renderer = ObservingNetworkCSVRenderer()
        result = renderer._format_list_field(['Atmosphere', 'Land', 'Ocean'])
        self.assertEqual(result, 'Atmosphere, Land, Ocean')

    def test_format_list_field_empty(self):
        """Test that empty list returns empty string."""
        renderer = ObservingNetworkCSVRenderer()
        result = renderer._format_list_field([])
        self.assertEqual(result, '')

    def test_format_list_field_none(self):
        """Test that None list returns empty string."""
        renderer = ObservingNetworkCSVRenderer()
        result = renderer._format_list_field(None)
        self.assertEqual(result, '')

    def test_format_streamfield_values(self):
        """Test extraction of values from StreamField data."""
        renderer = ObservingNetworkCSVRenderer()
        streamfield_data = [
            {'type': 'url', 'value': 'https://example.com'},
            {'type': 'url', 'value': 'https://other.com'},
        ]
        result = renderer._format_streamfield_values(streamfield_data)
        self.assertEqual(result, 'https://example.com, https://other.com')

    def test_format_streamfield_values_empty(self):
        """Test empty StreamField returns empty string."""
        renderer = ObservingNetworkCSVRenderer()
        result = renderer._format_streamfield_values([])
        self.assertEqual(result, '')

    def test_format_geometry_field(self):
        """Test formatting of geometry_field with bounding boxes."""
        renderer = ObservingNetworkCSVRenderer()
        geometry_data = [
            {
                'type': 'bounding_box',
                'value': {
                    'southwest': {'latitude': 45.0, 'longitude': -120.5},
                    'northeast': {'latitude': 50.0, 'longitude': -110.0},
                }
            }
        ]
        result = renderer._format_geometry_field(geometry_data)
        self.assertEqual(result, '45.0 -120.5 50.0 -110.0')

    def test_format_geometry_field_multiple_boxes(self):
        """Test formatting of multiple bounding boxes (comma-separated)."""
        renderer = ObservingNetworkCSVRenderer()
        geometry_data = [
            {
                'type': 'bounding_box',
                'value': {
                    'southwest': {'latitude': 45.0, 'longitude': -120.5},
                    'northeast': {'latitude': 50.0, 'longitude': -110.0},
                }
            },
            {
                'type': 'bounding_box',
                'value': {
                    'southwest': {'latitude': 60.0, 'longitude': -80.0},
                    'northeast': {'latitude': 70.0, 'longitude': -60.0},
                }
            }
        ]
        result = renderer._format_geometry_field(geometry_data)
        self.assertEqual(result, '45.0 -120.5 50.0 -110.0, 60.0 -80.0 70.0 -60.0')

    def test_format_geometry_field_empty(self):
        """Test empty geometry_field returns empty string."""
        renderer = ObservingNetworkCSVRenderer()
        result = renderer._format_geometry_field([])
        self.assertEqual(result, '')


class BlockCSVValueTests(TestCase):
    """Unit tests for block-level to_csv_value() methods."""

    def test_geopoint_block_to_csv_value(self):
        """Test GeoPointBlock returns 'lat lon' format."""
        block = GeoPointBlock()
        value = {'latitude': 45.5, 'longitude': -122.7}
        result = block.to_csv_value(value)
        self.assertEqual(result, '45.5 -122.7')

    def test_geopoint_block_to_csv_value_empty(self):
        """Test GeoPointBlock returns empty string for empty value."""
        block = GeoPointBlock()
        result = block.to_csv_value({})
        self.assertEqual(result, '')

    def test_geopoint_block_to_csv_value_none(self):
        """Test GeoPointBlock returns empty string for None."""
        block = GeoPointBlock()
        result = block.to_csv_value(None)
        self.assertEqual(result, '')

    def test_soso_bounding_box_to_csv_value(self):
        """Test SOSOBoundingBoxBlock returns correct format."""
        block = SOSOBoundingBoxBlock()
        value = {
            'southwest': {'latitude': 45.0, 'longitude': -120.5},
            'northeast': {'latitude': 50.0, 'longitude': -110.0},
        }
        result = block.to_csv_value(value)
        self.assertEqual(result, '45.0 -120.5 50.0 -110.0')

    def test_soso_bounding_box_to_csv_value_empty(self):
        """Test SOSOBoundingBoxBlock returns empty for empty value."""
        block = SOSOBoundingBoxBlock()
        result = block.to_csv_value({})
        self.assertEqual(result, '')

    def test_soso_bounding_box_to_csv_value_partial(self):
        """Test SOSOBoundingBoxBlock returns empty for partial value."""
        block = SOSOBoundingBoxBlock()
        value = {
            'southwest': {'latitude': 45.0, 'longitude': -120.5},
            'northeast': {},  # Missing coordinates
        }
        result = block.to_csv_value(value)
        self.assertEqual(result, '')

    def test_network_id_block_to_csv_value(self):
        """Test NetworkIdBlock returns value as-is."""
        block = NetworkIdBlock()
        result = block.to_csv_value('NOAA-12345')
        self.assertEqual(result, 'NOAA-12345')

    def test_network_id_block_to_csv_value_none(self):
        """Test NetworkIdBlock returns empty for None."""
        block = NetworkIdBlock()
        result = block.to_csv_value(None)
        self.assertEqual(result, '')


class CSVExportAPITests(WagtailPageTestCase):
    """Integration tests for CSV export via the API."""

    def setUp(self):
        self.client = APIClient()

        # Create page structure
        self.home_page = Page.objects.get(slug='home')
        self.index_page = ObservingNetworkIndexPage(title='Observing Networks')
        self.home_page.add_child(instance=self.index_page)
        self.index_page.save_revision().publish()

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password'
        )

        # Create controlled vocabulary items
        self.domain1 = Domain.objects.create(name='Atmosphere')
        self.domain2 = Domain.objects.create(name='Ocean')
        self.discipline1 = Discipline.objects.create(name='Meteorology')
        self.region1 = Region.objects.create(name='Arctic')

        # Create a test network with various field types
        self.network1 = ObservingNetworkPage(
            title='Test Network 1',
            name='Test Network 1',
            abbreviation='TN1',
            description='A test network for CSV export',
            website_url='https://example.com/network1',
            contact='contact@example.com',
            has_catalog='yes',
            metadata_access='yes',
            machine_readable='yes',
            start_year=2020,
            owner=self.user,
        )
        self.index_page.add_child(instance=self.network1)
        self.network1.domains.add(self.domain1, self.domain2)
        self.network1.disciplines.add(self.discipline1)
        self.network1.regions.add(self.region1)
        self.network1.save_revision().publish()

        # Create a second network for pagination tests
        self.network2 = ObservingNetworkPage(
            title='Test Network 2',
            name='Test Network 2',
            abbreviation='TN2',
            description='Another test network',
            website_url='https://example.com/network2',
            contact='contact2@example.com',
            has_catalog='no',
            owner=self.user,
        )
        self.index_page.add_child(instance=self.network2)
        self.network2.save_revision().publish()

    def test_csv_format_returns_csv_content_type(self):
        """Test that ?format=csv returns text/csv content type."""
        response = self.client.get('/api/v2/networks/?format=csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')

    def test_json_format_still_works(self):
        """Test that default JSON format still works."""
        response = self.client.get('/api/v2/networks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response['Content-Type'])

    def test_csv_export_contains_header_row(self):
        """Test that CSV export includes header row."""
        response = self.client.get('/api/v2/networks/?format=csv')
        content = response.content.decode('utf-8')
        reader = csv.reader(StringIO(content))
        rows = list(reader)

        self.assertGreater(len(rows), 0)
        # Check header row contains expected columns
        header = rows[0]
        self.assertIn('name', header)
        self.assertIn('abbreviation', header)
        self.assertIn('ropon_id', header)

    def test_csv_export_excludes_logo_image(self):
        """Test that logo_image is NOT in CSV columns (requirement #7)."""
        response = self.client.get('/api/v2/networks/?format=csv')
        content = response.content.decode('utf-8')
        reader = csv.reader(StringIO(content))
        header = next(reader)

        self.assertNotIn('logo_image', header)

    def test_csv_export_contains_all_records(self):
        """Test that CSV export returns ALL records (no pagination)."""
        response = self.client.get('/api/v2/networks/?format=csv')
        content = response.content.decode('utf-8')
        reader = csv.reader(StringIO(content))
        rows = list(reader)

        # Should have header + 2 networks
        self.assertEqual(len(rows), 3)

    def test_csv_m2m_fields_comma_separated(self):
        """Test that M2M fields are rendered as comma-separated values."""
        response = self.client.get('/api/v2/networks/?format=csv')
        content = response.content.decode('utf-8')
        reader = csv.DictReader(StringIO(content))
        rows = list(reader)

        # Find the row for network1 which has multiple domains
        network1_row = next(r for r in rows if r['name'] == 'Test Network 1')

        # domains should contain both values
        self.assertIn('Atmosphere', network1_row['domains'])
        self.assertIn('Ocean', network1_row['domains'])
        # Should be comma-separated
        self.assertIn(', ', network1_row['domains'])

    def test_csv_choice_fields_display_values(self):
        """Test that choice fields show display values, not raw values."""
        response = self.client.get('/api/v2/networks/?format=csv')
        content = response.content.decode('utf-8')
        reader = csv.DictReader(StringIO(content))
        rows = list(reader)

        network1_row = next(r for r in rows if r['name'] == 'Test Network 1')
        # has_catalog should show 'Yes' not 'yes'
        self.assertEqual(network1_row['has_catalog'], 'Yes')

    def test_csv_empty_fields(self):
        """Test handling of empty/null fields."""
        response = self.client.get('/api/v2/networks/?format=csv')
        content = response.content.decode('utf-8')
        reader = csv.DictReader(StringIO(content))
        rows = list(reader)

        # network2 has minimal fields - check empty fields are handled
        network2_row = next(r for r in rows if r['name'] == 'Test Network 2')

        # Empty M2M fields should be empty strings
        self.assertEqual(network2_row['disciplines'], '')

    def test_detail_view_rejects_csv_format(self):
        """Test that detail view returns 400 for CSV format."""
        response = self.client.get(
            f'/api/v2/networks/{self.network1.pk}/?format=csv'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_detail_view_json_still_works(self):
        """Test that detail view still works with JSON format."""
        response = self.client.get(f'/api/v2/networks/{self.network1.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_csv_special_characters_escaped(self):
        """Test that special characters in values are properly escaped."""
        from django.core.cache import cache

        # Update existing network with special characters
        # Note: In Wagtail, 'name' may be synced with 'title', so update both
        self.network1.title = 'Network with, commas'
        self.network1.name = 'Network with, commas'
        self.network1.description = 'Description with "quotes" and, commas'
        self.network1.save_revision().publish()

        # Clear cache to ensure fresh data
        cache.clear()

        response = self.client.get('/api/v2/networks/?format=csv')
        content = response.content.decode('utf-8')

        # CSV module should properly escape these - verify parsing works
        reader = csv.DictReader(StringIO(content))
        rows = list(reader)

        # Should still have 2 networks (CSV parsing didn't break due to commas/quotes)
        self.assertEqual(len(rows), 2)

        # Find row with special characters in description
        special_row = next(
            (r for r in rows if r.get('description') and 'quotes' in r['description']),
            None
        )
        self.assertIsNotNone(special_row)
        # Verify special characters are preserved correctly (CSV escapes quotes as "")
        self.assertEqual(special_row['description'], 'Description with "quotes" and, commas')

    def test_csv_empty_database(self):
        """Test CSV export with no networks."""
        from django.core.cache import cache

        try:
            # Unpublish all networks at once (set live=False)
            ObservingNetworkPage.objects.update(live=False)

            # Clear Django cache
            cache.clear()

            response = self.client.get('/api/v2/networks/?format=csv')
            self.assertEqual(response.status_code, 200)

            content = response.content.decode('utf-8')
            reader = csv.reader(StringIO(content))
            rows = list(reader)

            # Should have header row only (no live pages)
            self.assertEqual(len(rows), 1)
        finally:
            # Restore state for other tests - republish all networks
            ObservingNetworkPage.objects.update(live=True)
            cache.clear()
