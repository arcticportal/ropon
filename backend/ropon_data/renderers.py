"""


Provides CSV export functionality for the networks listing endpoint.
"""
import csv
from io import StringIO
from rest_framework.renderers import BaseRenderer

from ropon_data.blocks import SOSOBoundingBoxBlock


class ObservingNetworkCSVRenderer(BaseRenderer):
    """
    CSV Renderer for ObservingNetworkPage API responses.

    Handles:
    - Flattening nested data structures
    - Converting M2M fields to comma-separated strings
    - Formatting geometry_field bounding boxes using block-level serialization
    - Extracting StreamField values

    Note: This renderer is only intended for list views. Detail views
    should return JSON format only.
    """
    media_type = 'text/csv'
    format = 'csv'
    charset = 'utf-8'

    # CSV columns in order (excludes logo_image per requirement #7)
    CSV_COLUMNS = [
        'name',
        'abbreviation',
        'ropon_id',
        'description',
        'website_url',
        'logo_url',
        'organization_name',
        'domains',
        'disciplines',
        'regions',
        'subregions',
        'geometry_field',
        'start_year',
        'contact',
        'data_repository_url',
        'network_id',
        'asset_types',
        'has_catalog',
        'metadata_access',
        'machine_readable',
        'metadata_standards',
        'access_protocols',
        'metadata_catalog_url',
        'detail_url',
        'date_last_modified',
    ]

    # Fields that come from 'meta' object in the API response
    META_FIELDS = {
        'detail_url',
        'date_last_modified',
    }

    # Fields that contain lists (M2M relationships)
    LIST_FIELDS = {
        'organization_name',
        'domains',
        'disciplines',
        'regions',
        'subregions',
        'asset_types',
        'metadata_standards',
        'access_protocols',
    }

    # StreamFields that need value extraction (non-geometry)
    STREAMFIELD_VALUE_FIELDS = {
        'data_repository_url',
        'network_id',
        'metadata_catalog_url',
    }

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render data as CSV.

        Args:
            data: List of serialized ObservingNetworkPage items
            accepted_media_type: The negotiated media type
            renderer_context: Context dictionary with view, request, etc.

        Returns:
            CSV formatted string
        """
        if data is None or (isinstance(data, list) and len(data) == 0):
            # Return empty CSV with headers only
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=self.CSV_COLUMNS)
            writer.writeheader()
            return output.getvalue()

        # Ensure data is a list
        if not isinstance(data, list):
            data = [data]

        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=self.CSV_COLUMNS,
            extrasaction='ignore'
        )
        writer.writeheader()

        for item in data:
            row = self._flatten_item(item)
            writer.writerow(row)

        return output.getvalue()

    def _flatten_item(self, item):
        """
        Flatten a single ObservingNetworkPage item for CSV export.

        Args:
            item: Dictionary of serialized page data

        Returns:
            Dictionary with flattened values suitable for CSV
        """
        row = {}
        meta = item.get('meta', {})

        for col in self.CSV_COLUMNS:
            # Check if field comes from meta object
            if col in self.META_FIELDS:
                value = meta.get(col)
            else:
                value = item.get(col)

            if value is None:
                row[col] = ''
            elif col == 'geometry_field':
                row[col] = self._format_geometry_field(value)
            elif col in self.STREAMFIELD_VALUE_FIELDS:
                row[col] = self._format_streamfield_values(value)
            elif col in self.LIST_FIELDS:
                row[col] = self._format_list_field(value)
            else:
                row[col] = self._format_simple_value(value)

        return row

    def _format_geometry_field(self, geometry_data):
        """
        Format geometry_field bounding boxes using block-level serialization.

        Format: "sw.lat sw.lon ne.lat ne.lon"
        Multiple boxes separated by ", "

        Args:
            geometry_data: List of bounding box blocks from StreamField

        Returns:
            Formatted string of bounding boxes
        """
        if not geometry_data:
            return ''

        formatted_boxes = []
        block_instance = SOSOBoundingBoxBlock()

        for block in geometry_data:
            if isinstance(block, dict) and block.get('type') == 'bounding_box':
                value = block.get('value', {})
                formatted = block_instance.to_csv_value(value)
                if formatted:
                    formatted_boxes.append(formatted)

        return ', '.join(formatted_boxes)

    def _format_streamfield_values(self, streamfield_data):
        """
        Extract and join values from StreamFields.

        Args:
            streamfield_data: List of blocks from StreamField

        Returns:
            Comma-separated string of values
        """
        if not streamfield_data:
            return ''

        values = []
        for block in streamfield_data:
            if isinstance(block, dict):
                value = block.get('value', '')
                if value:
                    values.append(str(value))

        return ', '.join(values)

    def _format_list_field(self, value):
        """
        Format list/M2M fields as comma-separated strings.

        Args:
            value: List of string values

        Returns:
            Comma-separated string
        """
        if not value:
            return ''

        if isinstance(value, list):
            return ', '.join(str(v) for v in value if v)

        return str(value)

    def _format_simple_value(self, value):
        """
        Format simple field values.

        Args:
            value: Field value

        Returns:
            String representation
        """
        if value is None:
            return ''
        return str(value)
