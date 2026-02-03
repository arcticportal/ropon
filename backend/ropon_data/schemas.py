"""
OpenAPI schema postprocessing handlers for ropon_data endpoints.

This module contains postprocessing handlers that customize the OpenAPI schema
for ropon_data API endpoints. These are called by ropon.schema.postprocessing_hook.

Why postprocessing handlers instead of decorators?
    Wagtail's API viewsets use non-standard method names (listing_view, detail_view)
    that drf-spectacular's @extend_schema_view decorator doesn't recognize.
    Postprocessing handlers modify the schema after generation, which works reliably.

Usage:
    # In ropon.schema._apply_endpoint_schemas():
    from ropon_data.schemas import apply_networks_schema, apply_cv_schema
    apply_networks_schema(paths)
    apply_cv_schema(paths)

    # In ropon.schema._apply_component_schemas():
    from ropon_data.schemas import get_networks_component_schemas
    schemas.update(get_networks_component_schemas())
"""


# =============================================================================
# Component Schemas for Networks
# =============================================================================

def get_networks_component_schemas() -> dict:
    """
    Return component schemas for Networks endpoints.

    Uses auto-generated schemas from model and block classes where possible,
    with manual definitions only for Wagtail-specific wrappers.

    Returns:
        Dict of schema name -> schema definition to add to components/schemas.
    """
    from ropon_data.models import ObservingNetworkPage
    from ropon_data.blocks import SOSOBoundingBoxBlock, NetworkIdBlock, get_url_block_schema

    return {
        # Auto-generated from model (combines Django fields + StreamField blocks)
        'ObservingNetwork': ObservingNetworkPage.get_openapi_schema(),

        # Auto-generated from block classes (with StreamField wrapper format)
        'SOSOBoundingBox': SOSOBoundingBoxBlock.get_openapi_schema(include_streamfield_wrapper=True),
        # 'NetworkIdBlock': NetworkIdBlock.get_openapi_schema(),
        # 'UrlBlock': get_url_block_schema('url'),

        # Wagtail-specific wrappers (manual - not introspectable from model)
        'ObservingNetworkMeta': {
            'type': 'object',
            'description': 'Metadata about the Observing Network resource.',
            'properties': {
                'detail_url': {
                    'type': 'string',
                    'format': 'uri',
                    'description': 'URL to retrieve the full details of this network.',
                    'example': 'https://api.example.org/api/v2/networks/fd742245-233c-4e47-b7df-13d1208025aa/'
                },
                'first_published_at': {
                    'type': 'string',
                    'format': 'date-time',
                    'description': 'Timestamp when the network was first published.',
                    'example': '2025-05-15T10:10:57.345000Z'
                },
                'date_last_modified': {
                    'type': 'string',
                    'format': 'date-time',
                    'description': 'Timestamp when the network was last modified.',
                    'example': '2025-10-10T14:23:02.573619Z'
                }
            }
        },

        # 'LogoImage': {
        #     'type': 'object',
        #     'nullable': True,
        #     'description': 'Logo image associated with the network.',
        #     'properties': {
        #         'id': {
        #             'type': 'integer',
        #             'description': 'Image ID.'
        #         },
        #         'meta': {
        #             'type': 'object',
        #             'properties': {
        #                 'type': {
        #                     'type': 'string',
        #                     'example': 'wagtailimages.Image'
        #                 },
        #                 'detail_url': {
        #                     'type': 'string',
        #                     'format': 'uri'
        #                 },
        #                 'download_url': {
        #                     'type': 'string',
        #                     'format': 'uri'
        #                 }
        #             }
        #         },
        #         'title': {
        #             'type': 'string',
        #             'description': 'Image title.'
        #         },
        #         'width': {
        #             'type': 'integer',
        #             'description': 'Image width in pixels.'
        #         },
        #         'height': {
        #             'type': 'integer',
        #             'description': 'Image height in pixels.'
        #         }
        #     }
        # },

        # List response wrapper
        'ObservingNetworkListResponse': {
            'type': 'object',
            'description': 'Paginated list of Observing Networks.',
            'properties': {
                'meta': {
                    'type': 'object',
                    'properties': {
                        'total_count': {
                            'type': 'integer',
                            'description': 'Total number of networks available.'
                        }
                    }
                },
                'items': {
                    'type': 'array',
                    'items': {'$ref': '#/components/schemas/ObservingNetwork'},
                    'description': 'List of observing networks.'
                }
            }
        }
    }


# =============================================================================
# Networks Endpoint Schema (/api/v2/networks/)
# =============================================================================

def apply_networks_schema(paths: dict) -> None:
    """
    Apply schema customizations for /api/v2/networks/ endpoints.

    Args:
        paths: The OpenAPI paths dict to modify in place.
    """
    # Networks list endpoint: /api/v2/networks/
    if '/api/v2/networks/' in paths:
        networks_list = paths['/api/v2/networks/'].get('get', {})
        networks_list['tags'] = ['Networks']
        networks_list['summary'] = 'List all Observing Networks'
        networks_list['description'] = """Returns a paginated list of all Observing Networks registered in RoPON.

**Query Parameters:**
- `format`: Response format (`json` or `csv`). CSV exports all records without pagination.
- `fields`: Comma-separated list of fields to include (e.g., `name,ropon_id,abbreviation`). Use `*` for all fields.
- `limit`: Number of results per page (default: 20).
- `offset`: Pagination offset.
- `order`: Sort order for results.

**CSV Export:** Use `?format=csv` to download all networks as a CSV file."""

        networks_list['parameters'] = [
            {
                'name': 'format',
                'in': 'query',
                'description': 'Response format. Use `csv` for CSV export (list view only).',
                'schema': {'type': 'string', 'enum': ['json', 'csv']}
            },
            {
                'name': 'fields',
                'in': 'query',
                'description': 'Comma-separated list of fields to include. Use `*` for all fields.',
                'schema': {'type': 'string'}
            },
            {
                'name': 'limit',
                'in': 'query',
                'description': 'Number of results per page (default: 20).',
                'schema': {'type': 'integer'}
            },
            {
                'name': 'offset',
                'in': 'query',
                'description': 'Pagination offset.',
                'schema': {'type': 'integer'}
            },
            {
                'name': 'order',
                'in': 'query',
                'description': 'Sort order (e.g., `name`, `-name` for descending).',
                'schema': {'type': 'string'}
            },
        ]

        # Add response schema
        networks_list['responses'] = {
            '200': {
                'description': 'Successful response with list of observing networks.',
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/ObservingNetworkListResponse'}
                    }
                }
            }
        }

    # Networks detail by ropon_id: /api/v2/networks/{ropon_id}/
    if '/api/v2/networks/{ropon_id}/' in paths:
        networks_ropon = paths['/api/v2/networks/{ropon_id}/'].get('get', {})
        networks_ropon['tags'] = ['Networks']
        networks_ropon['summary'] = 'Get Observing Network by RoPON ID'
        networks_ropon['description'] = """Returns a single Observing Network by its RoPON ID (UUID).

**Response Format:** JSON only. CSV format is not supported for detail views. Use the list endpoint for CSV export.

**Query Parameters:**
- `fields`: Comma-separated list of fields to include in the response."""

        networks_ropon['parameters'] = [
            {
                'name': 'ropon_id',
                'in': 'path',
                'required': True,
                'description': 'Unique identifier for the observing network (UUID format, e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`).',
                'schema': {
                    'type': 'string',
                    'format': 'uuid',
                    'maxLength': 255
                }
            },
            {
                'name': 'fields',
                'in': 'query',
                'description': 'Comma-separated list of fields to include. Use `*` for all fields.',
                'schema': {'type': 'string'}
            },
        ]

        # Add response schema
        networks_ropon['responses'] = {
            '200': {
                'description': 'Successful response with observing network details.',
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/ObservingNetwork'}
                    }
                }
            },
            '404': {
                'description': 'Network not found.',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'message': {
                                    'type': 'string',
                                    'example': 'not found'
                                }
                            }
                        }
                    }
                }
            }
        }


# =============================================================================
# Controlled Vocabularies Endpoint Schema (/api/v2/cv/)
# =============================================================================

def get_cv_component_schemas() -> dict:
    """
    Return component schemas for CV endpoints.

    Returns:
        Dict of schema name -> schema definition to add to components/schemas.
    """
    # TODO: Add CV schemas when needed
    return {}


def apply_cv_schema(paths: dict) -> None:
    """
    Apply schema customizations for /api/v2/cv/ endpoints.

    Args:
        paths: The OpenAPI paths dict to modify in place.

    Note: Currently a stub. Implement when CV documentation is needed.
    """
    # TODO: Add CV endpoint schema customizations when needed
    pass
