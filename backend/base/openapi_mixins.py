"""
OpenAPI schema generation mixins for Wagtail blocks and Django models.

This module provides reusable mixins that auto-generate OpenAPI schemas
by introspecting class definitions:
- OpenAPIBlockMixin: For Wagtail blocks (uses child_blocks)
- OpenAPIModelMixin: For Django/Wagtail models (uses _meta.fields)
"""

from wagtail.blocks import (
    CharBlock, TextBlock, URLBlock,
    FloatBlock, IntegerBlock, BooleanBlock
)
from wagtail.fields import StreamField


class OpenAPIBlockMixin:
    """
    Mixin for Wagtail blocks that auto-generates OpenAPI schemas.

    Uses child_blocks introspection for StructBlocks.
    Supports nested blocks by recursively calling get_openapi_schema().
    """

    # Block type -> OpenAPI type mapping
    BLOCK_TYPE_MAP = {
        CharBlock: {'type': 'string'},
        TextBlock: {'type': 'string'},
        URLBlock: {'type': 'string', 'format': 'uri'},
        FloatBlock: {'type': 'number', 'format': 'float'},
        IntegerBlock: {'type': 'integer'},
        BooleanBlock: {'type': 'boolean'},
    }

    # Validator name -> constraints mapping (for known validators)
    VALIDATOR_CONSTRAINTS = {
        'validate_latitude': {'minimum': -90, 'maximum': 90},
        'validate_longitude': {'minimum': -180, 'maximum': 180},
    }

    @classmethod
    def get_openapi_schema(cls, include_streamfield_wrapper: bool = False) -> dict:
        """
        Generate OpenAPI schema by introspecting child_blocks.

        Args:
            include_streamfield_wrapper: If True, wrap in StreamField format
                                         with type/value/id structure

        Returns:
            OpenAPI schema dict
        """
        block_instance = cls()
        properties = {}

        # Introspect child_blocks for StructBlock
        if hasattr(block_instance, 'child_blocks'):
            for field_name, child_block in block_instance.child_blocks.items():
                properties[field_name] = cls._block_to_schema(child_block, include_streamfield_wrapper)

        schema = {
            'type': 'object',
            'description': getattr(cls._meta_class, 'label', cls.__name__) if hasattr(cls, '_meta_class') else cls.__name__,
            'properties': properties
        }

        # Optionally wrap in StreamField format
        if include_streamfield_wrapper:
            block_type_name = cls.__name__.lower().replace('block', '')
            return {
                'type': 'object',
                'description': schema['description'],
                'properties': {
                    'type': {'type': 'string', 'enum': [cls.__name__]},
                    'value': schema,
                    'id': {'type': 'string', 'format': 'uuid'}
                }
            }

        return schema

    @classmethod
    def _block_to_schema(cls, block, include_streamfield_wrapper=False) -> dict:
        """Convert a single block to OpenAPI schema."""
        # If child block has its own get_openapi_schema, use it (recursion)
        if hasattr(block, 'get_openapi_schema') and callable(block.get_openapi_schema):
            return block.get_openapi_schema(include_streamfield_wrapper=include_streamfield_wrapper)
        # Map known block types
        for known_type, schema in cls.BLOCK_TYPE_MAP.items():
            if isinstance(block, known_type):
                result = schema.copy()

                # Extract constraints from validators
                if hasattr(block, 'validators'):
                    for validator in block.validators:
                        validator_name = getattr(validator, '__name__', '')
                        if validator_name in cls.VALIDATOR_CONSTRAINTS:
                            result.update(cls.VALIDATOR_CONSTRAINTS[validator_name])

                # Add label as description
                if hasattr(block, 'label') and block.label:
                    result['description'] = block.label

                return result

        # Fallback
        return {'type': 'string'}


class OpenAPIModelMixin:
    """
    Mixin for Django models that auto-generates OpenAPI schemas.

    Uses _meta.fields introspection for Django fields.
    Calls get_openapi_schema() on StreamField blocks for nested schemas.

    Configuration class attributes (override in subclasses):
        EXTRA_EXCLUDED_FIELDS: Set of additional field names to exclude
        INCLUDE_FIELDS: Set of field names to always include (overrides exclusions)
        M2M_SERIALIZATION_MODE: How M2M fields are serialized ('string_array' or 'object_array')
        SKIP_STREAMFIELDS: If True, skip StreamField auto-generation (handle manually)
        SKIP_FOREIGNKEYS: If True, skip ForeignKey auto-generation (handle manually)

    Customization hooks (override in subclasses):
        _add_custom_properties(properties): Add model-specific properties after auto-generation
    """

    # Django field type -> OpenAPI type mapping
    FIELD_TYPE_MAP = {
        'CharField': {'type': 'string'},
        'TextField': {'type': 'string'},
        'URLField': {'type': 'string', 'format': 'uri'},
        'EmailField': {'type': 'string', 'format': 'email'},
        'UUIDField': {'type': 'string', 'format': 'uuid'},
        'IntegerField': {'type': 'integer'},
        'FloatField': {'type': 'number', 'format': 'float'},
        'BooleanField': {'type': 'boolean'},
        'DateField': {'type': 'string', 'format': 'date'},
        'DateTimeField': {'type': 'string', 'format': 'date-time'},
    }

    # Base fields to exclude from auto-generation (Wagtail/Django internals)
    BASE_EXCLUDED_FIELDS = {
        'pk', 'page_ptr', 'content_type', 'path', 'depth',
        'numchild', 'translation_key', 'locale', 'alias_of',
        'draft_title', 'has_unpublished_changes', 'expired',
        'expire_at', 'go_live_at', 'live', 'locked', 'locked_at',
        'locked_by', 'latest_revision', 'live_revision', 'latest_revision_created_at',
        'revision', 'workflow_states',
        'aliases', 'revisions', 'subscribers', 'comments',
        'sites_rooted_here', 'aliases_of_me', 'group_permissions',
        'view_restrictions', 'url_path', 'owner', 'first_published_at', 'last_published_at',
        'slug', 'seo_title', 'show_in_menus', 'search_description',
    }

    # Additional fields to exclude (override in subclasses)
    EXTRA_EXCLUDED_FIELDS: set = set()

    # Fields to explicitly include even if in exclusion lists
    INCLUDE_FIELDS: set = {'id'}

    # M2M serialization mode: 'string_array' (StringRelatedField) or 'object_array'
    M2M_SERIALIZATION_MODE: str = 'object_array'

    # Skip certain field types for manual handling
    SKIP_STREAMFIELDS: bool = False
    SKIP_FOREIGNKEYS: bool = False

    # Legacy compatibility: keep EXCLUDED_FIELDS as alias
    @classmethod
    def _get_excluded_fields(cls) -> set:
        """Get combined set of excluded fields."""
        # Support both old EXCLUDED_FIELDS and new BASE_EXCLUDED_FIELDS + EXTRA_EXCLUDED_FIELDS
        excluded = cls.BASE_EXCLUDED_FIELDS.copy()
        excluded.update(cls.EXTRA_EXCLUDED_FIELDS)
        # Legacy support: if subclass defines EXCLUDED_FIELDS, use it
        if hasattr(cls, 'EXCLUDED_FIELDS') and cls.EXCLUDED_FIELDS != OpenAPIModelMixin.BASE_EXCLUDED_FIELDS:
            excluded.update(getattr(cls, 'EXCLUDED_FIELDS', set()))
        return excluded - cls.INCLUDE_FIELDS

    @classmethod
    def get_openapi_schema(cls) -> dict:
        """Generate OpenAPI schema by introspecting model fields."""
        properties = {}
        excluded = cls._get_excluded_fields()

        for field in cls._meta.get_fields():
            field_name = field.name

            # Skip excluded fields (unless explicitly included)
            if field_name in excluded and field_name not in cls.INCLUDE_FIELDS:
                continue

            # Skip reverse relations
            if field.is_relation and not field.concrete:
                continue

            schema = cls._field_to_schema(field)
            if schema:
                properties[field_name] = schema

        # Allow subclasses to add custom properties
        cls._add_custom_properties(properties)

        return {
            'type': 'object',
            'description': cls._meta.verbose_name or cls.__name__,
            'properties': properties
        }

    @classmethod
    def _add_custom_properties(cls, properties: dict) -> None:
        """
        Hook for subclasses to add model-specific properties.

        Override this method to add StreamField schemas with $ref,
        computed fields, or other custom properties.

        Args:
            properties: Dict to modify in place with additional properties.
        """
        pass  # Default: no custom properties

    @classmethod
    def _field_to_schema(cls, field) -> dict:
        """Convert a Django field to OpenAPI schema."""
        # Handle StreamField - delegate to block's schema
        if isinstance(field, StreamField):
            if cls.SKIP_STREAMFIELDS:
                return None  # Handle manually in _add_custom_properties
            # Get first block type for simplicity
            # (extend if multiple block types needed)
            if field.stream_block.child_blocks:
                block_name, block = list(field.stream_block.child_blocks.items())[0]
                if hasattr(block, 'get_openapi_schema'):
                    return {
                        'type': 'array',
                        'items': block.get_openapi_schema(include_streamfield_wrapper=True)
                    }
            return {'type': 'array', 'items': {'type': 'object'}}

        # Handle M2M relationships
        if field.many_to_many:
            if cls.M2M_SERIALIZATION_MODE == 'string_array':
                return {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': str(field.help_text) if hasattr(field, 'help_text') and field.help_text else f'{field.verbose_name} values.'
                }
            else:
                return {
                    'type': 'array',
                    'items': {'type': 'object'},
                    'description': f'{field.name} references'
                }

        # Handle ForeignKey
        if field.is_relation:
            if cls.SKIP_FOREIGNKEYS:
                return None  # Handle manually in _add_custom_properties
            return {'type': 'object', 'description': f'{field.name} reference'}

        # Handle choice fields -> enum
        if hasattr(field, 'choices') and field.choices:
            schema = {
                'type': 'string',
                'enum': [c[1] for c in field.choices],
            }
            if hasattr(field, 'help_text') and field.help_text:
                schema['description'] = str(field.help_text)
            return schema

        # Map standard Django fields
        internal_type = field.get_internal_type()
        if internal_type in cls.FIELD_TYPE_MAP:
            schema = cls.FIELD_TYPE_MAP[internal_type].copy()

            # Add max_length constraint
            if hasattr(field, 'max_length') and field.max_length:
                schema['maxLength'] = field.max_length

            # Add nullable support
            if hasattr(field, 'null') and field.null:
                schema['nullable'] = True

            # Add help_text as description
            if field.help_text:
                schema['description'] = str(field.help_text)

            return schema

        return None  # Unknown field type
