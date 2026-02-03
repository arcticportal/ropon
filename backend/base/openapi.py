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

    # Fields to exclude from auto-generation (Wagtail internals)
    EXCLUDED_FIELDS = {
        'id', 'pk', 'page_ptr', 'content_type', 'path', 'depth',
        'numchild', 'translation_key', 'locale', 'alias_of',
        'draft_title', 'has_unpublished_changes', 'expired',
        'expire_at', 'go_live_at', 'live', 'locked', 'locked_at',
        'locked_by', 'latest_revision', 'live_revision',
    }

    @classmethod
    def get_openapi_schema(cls) -> dict:
        """Generate OpenAPI schema by introspecting model fields."""
        properties = {}

        for field in cls._meta.get_fields():
            # Skip excluded fields
            if field.name in cls.EXCLUDED_FIELDS:
                continue

            # Skip reverse relations
            if field.is_relation and not field.concrete:
                continue

            schema = cls._field_to_schema(field)
            if schema:
                properties[field.name] = schema

        return {
            'type': 'object',
            'description': cls._meta.verbose_name or cls.__name__,
            'properties': properties
        }

    @classmethod
    def _field_to_schema(cls, field) -> dict:
        """Convert a Django field to OpenAPI schema."""
        # Handle StreamField - delegate to block's schema
        if isinstance(field, StreamField):
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
            return {
                'type': 'array',
                'items': {'type': 'object'},
                'description': f'{field.name} references'
            }

        # Handle ForeignKey
        if field.is_relation:
            return {'type': 'object', 'description': f'{field.name} reference'}

        # Map standard Django fields
        internal_type = field.get_internal_type()
        if internal_type in cls.FIELD_TYPE_MAP:
            schema = cls.FIELD_TYPE_MAP[internal_type].copy()

            # Add max_length constraint
            if hasattr(field, 'max_length') and field.max_length:
                schema['maxLength'] = field.max_length

            # Add help_text as description
            if field.help_text:
                schema['description'] = str(field.help_text)

            return schema

        return None  # Unknown field type
