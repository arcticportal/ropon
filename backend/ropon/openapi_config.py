"""
drf-spectacular preprocessing and postprocessing hooks for RoPON API.

This module provides the central schema configuration that orchestrates
endpoint-specific handlers from each app's openapi_schemas.py module.

Wagtail's API viewsets use non-standard method names (listing_view, detail_view)
that drf-spectacular's extend_schema_view doesn't handle well. We use postprocessing
hooks to apply the correct schema definitions after the schema is generated.

Architecture:
    - Preprocessing: Filter which endpoints appear in documentation
    - Postprocessing: Apply endpoint-specific documentation from app schemas
    - Each app (ropon_data, etc.) owns its own schema definitions
    - Custom AutoSchema: Handles operationId collisions for dual URL patterns
"""

from drf_spectacular.openapi import AutoSchema


# =============================================================================
# Custom AutoSchema Class
# =============================================================================

class RoponAutoSchema(AutoSchema):
    """
    Custom AutoSchema that generates unique operationIds based on path parameters.

    This prevents collisions between endpoints like:
    - /api/v2/networks/{id}/ -> networks_retrieve_by_id
    - /api/v2/networks/{ropon_id}/ -> networks_retrieve_by_ropon_id

    Without this, both would generate 'api_v2_networks_retrieve' causing collisions.
    """

    def get_operation_id(self):
        """
        Generate a unique operationId that includes path parameter names.
        """
        # Get the path from the view
        path = self.path

        # Extract path segments (excluding parameters)
        path_parts = [p for p in path.strip('/').split('/') if p and not p.startswith('{')]

        # Extract parameter names from path
        param_parts = []
        for p in path.strip('/').split('/'):
            if p.startswith('{') and p.endswith('}'):
                param_parts.append(p[1:-1])  # Extract param name without braces

        # Build base name from path (e.g., 'api/v2/networks' -> 'networks')
        base_name = path_parts[-1] if path_parts else 'root'

        # Determine action based on method and parameters
        method = self.method.lower()
        if method == 'get':
            if param_parts:
                # Detail view - include parameter name to avoid collisions
                action = f"retrieve_by_{'_'.join(param_parts)}"
            else:
                action = 'list'
        elif method == 'post':
            action = 'create'
        elif method == 'put':
            action = 'update'
        elif method == 'patch':
            action = 'partial_update'
        elif method == 'delete':
            action = 'destroy'
        else:
            action = method

        return f"{base_name}_{action}"

# =============================================================================
# Configuration
# =============================================================================

# Paths to include in documentation (prefix matching)
DOCUMENTED_PATHS = [
    '/api/v2/networks',
    # '/api/v2/cv',  # Uncomment when CV documentation is needed
]

# Paths to explicitly exclude even if they match DOCUMENTED_PATHS
EXCLUDED_PATHS = [
    '/api/v2/networks/find',
    '/api/v2/networks/{id}',
]


# =============================================================================
# Preprocessing Hook
# =============================================================================

def preprocessing_filter_spec(endpoints):
    """
    Filter endpoints to only include those we want to document.

    This runs before schema generation to exclude unwanted endpoints.

    Args:
        endpoints: List of (path, path_regex, method, callback) tuples.

    Returns:
        Filtered list of endpoints.
    """
    filtered = []
    for (path, path_regex, method, callback) in endpoints:
        # Include only paths that start with documented paths
        if any(path.startswith(doc_path) for doc_path in DOCUMENTED_PATHS):
            # But exclude specific paths we don't want
            if not any(path.startswith(excl_path) for excl_path in EXCLUDED_PATHS):
                filtered.append((path, path_regex, method, callback))

    return filtered


# =============================================================================
# Postprocessing Hook
# =============================================================================

def postprocessing_hook(result, generator, request, public):
    """
    Post-process the generated OpenAPI schema.

    This orchestrates endpoint-specific schema handlers from each app.

    Args:
        result: The generated OpenAPI schema dict.
        generator: The schema generator instance.
        request: The HTTP request (if any).
        public: Whether this is a public schema.

    Returns:
        The modified schema dict.
    """
    paths = result.get('paths', {})

    # Remove any paths that slipped through preprocessing
    _remove_excluded_paths(paths)

    # Apply component schemas (response models, etc.)
    _apply_component_schemas(result)

    # Apply endpoint-specific schema customizations
    _apply_endpoint_schemas(paths)

    # Clean up auto-generated tags
    _cleanup_tags(result)

    return result


def _remove_excluded_paths(paths: dict) -> None:
    """Remove paths that should not appear in documentation."""
    paths_to_remove = ['/api/v2/networks/{id}/']
    for path in paths_to_remove:
        if path in paths:
            del paths[path]


def _apply_component_schemas(result: dict) -> None:
    """
    Apply component schemas (response models, nested objects, etc.).

    Import and call schema getters from each app's schemas module.
    These define the reusable schema components in the OpenAPI spec.
    """
    # Ensure components/schemas exists
    if 'components' not in result:
        result['components'] = {}
    if 'schemas' not in result['components']:
        result['components']['schemas'] = {}

    schemas = result['components']['schemas']

    # Networks schemas (ropon_data app)
    from ropon_data.openapi_schemas import get_networks_component_schemas
    schemas.update(get_networks_component_schemas())

    # Controlled Vocabularies schemas (ropon_data app)
    # Uncomment when CV documentation is needed:
    # from ropon_data.openapi_schemas import get_cv_component_schemas
    # schemas.update(get_cv_component_schemas())


def _apply_endpoint_schemas(paths: dict) -> None:
    """
    Apply endpoint-specific schema customizations.

    Import and call handlers from each app's schemas module.
    Add new handlers here as more endpoints are documented.
    """
    # Networks endpoints (ropon_data app)
    from ropon_data.openapi_schemas import apply_networks_schema
    apply_networks_schema(paths)

    # Controlled Vocabularies endpoints (ropon_data app)
    # Uncomment when CV documentation is needed:
    # from ropon_data.openapi_schemas import apply_cv_schema
    # apply_cv_schema(paths)


def _cleanup_tags(result: dict) -> None:
    """Remove auto-generated tags that shouldn't appear."""
    if 'tags' in result:
        # Remove the default 'api' tag that drf-spectacular adds for untagged endpoints
        result['tags'] = [
            tag for tag in result['tags']
            if tag.get('name') != 'api'
        ]
