# ropon_data/models.py

import uuid
import os
import requests
from io import BytesIO
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.core.files.images import ImageFile
from django.utils.html import format_html
from django.template.loader import render_to_string
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from rest_framework import serializers
from ropon_data.blocks import SOSOBoundingBoxBlock, NetworkIdBlock
from wagtail import blocks
from wagtail.admin.panels import (FieldPanel, MultiFieldPanel,
                                  MultipleChooserPanel, ObjectList, HelpPanel,
                                  TabbedInterface)
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.images.models import Image
from wagtail.search import index
from flags.state import flag_enabled

from .validators import validate_email_or_url, validate_start_year, validate_image_url
from django.conf import settings
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError


User = get_user_model()


def get_observing_network_help_content():
    """
    Get the help content for the observing network page from template.
    
    This function renders the help panel template. The template uses the
    existing frontend_url template tag to get the frontend URL.
    
    Returns:
        str: The rendered HTML content for the help panel
    """
    # Render the template - no context needed as template uses frontend_url tag
    return render_to_string('ropon_data/help/observing_network_help.html')

FLAG_REMOVE_PREVIEW_OPTIONS = 'ROPON.REMOVE_PREVIEW_OPTIONS'
# ------ Controlled Vocabulary Models --------


# Base class for all controlled vocabulary models

class ControlledVocabularyModel(models.Model):
    """Base class for all controlled vocabulary models"""
    name = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0, help_text='Order for display. Use 0 for default ordering.')

    class Meta:
        abstract = True
        ordering = ['sort_order', 'id']

    panels = [FieldPanel('name'), 
                                FieldPanel('sort_order')]

    def __str__(self):
        return self.name
    
    api_fields = [
        APIField('name'),
        APIField('sort_order'),
    ]

class Domain(ControlledVocabularyModel):
    pass

class Discipline(ControlledVocabularyModel):
    pass

class Region(ControlledVocabularyModel):
    pass

class Subregion(ControlledVocabularyModel):
    pass

class AssetType(ControlledVocabularyModel):
    description = models.TextField(blank=True, null=True, verbose_name='Description', help_text='Description of the asset type, including examples of the types of assets that fall under this category.')
    panels = ControlledVocabularyModel.panels + [FieldPanel('description')]

    api_fields = ControlledVocabularyModel.api_fields + [
        APIField('description'),
    ]
class MetadataStandard(ControlledVocabularyModel):
    description = models.TextField(blank=True, null=True, verbose_name='Description', help_text='Description of the metadata standard, including examples of the types of metadata that fall under this category.')
    source_url = models.URLField(blank=True, null=True, verbose_name='Source URL', help_text='URL to the official documentation or website for the metadata standard.')
    panels = ControlledVocabularyModel.panels + [
        FieldPanel('description')] + [
        FieldPanel('source_url')]

    @property
    def source_url_link(self):
        if self.source_url:
            return format_html('<a href="{}" target="_blank">{}</a>', self.source_url, self.source_url)
        return ""

    source_url_link.fget.short_description = 'Source URL'

    api_fields = ControlledVocabularyModel.api_fields + [
        APIField('description'),
        APIField('source_url'),
    ]

class AccessProtocol(ControlledVocabularyModel):
    description = models.TextField(blank=True, null=True, verbose_name='Description', help_text='Description of the access protocol, including examples of the types of access protocols that fall under this category.')
    source_url = models.URLField(blank=True, null=True, verbose_name='Source URL', help_text='URL to the official documentation or website for the access protocol.')
    panels = ControlledVocabularyModel.panels + [
        FieldPanel('description')] + [
        FieldPanel('source_url')]
    @property
    def source_url_link(self):
        if self.source_url:
            return format_html('<a href="{}" target="_blank">{}</a>', self.source_url, self.source_url)
        return ""

    api_fields = ControlledVocabularyModel.api_fields + [
        APIField('description'),
        APIField('source_url'),
    ]

# ------ Observing Network Page Models --------


class Organization(index.Indexed, models.Model):
    name = models.CharField("Organization name", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    api_fields = [
        APIField('name'),
    ]

    panels = [FieldPanel('name')]
    search_fields = [
        index.SearchField('name'),
        index.AutocompleteField('name'),
        ]

class ObservingNetworkOrganization(Orderable,models.Model):
    observingnetwork = ParentalKey('ObservingNetworkPage', 
                                   related_name='network_organizations',
                                   on_delete=models.CASCADE)
    organization = models.ForeignKey(
        'ropon_data.Organization',
        on_delete=models.CASCADE,
        related_name='organizations_networks'
    )

    panels = [FieldPanel('organization')]

    api_fields = [
        APIField('organization'),
    ]

    def __str__(self):
        return self.organization.name

    class Meta:
        verbose_name = 'Observing Network Organization'
        verbose_name_plural = 'Observing Network Organizations'

    

class ObservingNetworkPage(Page):
    # Network information
    name = models.CharField(
        max_length=255, 
        verbose_name='Network Name',
        help_text='The full name of the observing network e.g. Svalbard Integrated Arctic Earth Observing System'
    )
    is_owner_authorized = models.BooleanField(
        default=False,
        editable=False
    )
    abbreviation = models.CharField(
        max_length=255,
        verbose_name='Network Abbreviation',
        help_text='Acronym or short name of the observing network. e.g. SIOS'
    )
    description = models.TextField(
        verbose_name='Network Description',
        help_text='Short summary of the observing network, including geographic or thematic scope.'
    )
    website_url = models.URLField(
        verbose_name='Network Website',
        help_text='URL to the observing network website'
    )
    logo_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Network Logo',
        help_text='URL to the observing network logo.(must be .png, .jpg, .jpeg or .svg format)'
        # validators=[validate_image_url]
    )

    logo_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    ropon_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='ROPON ID',
        help_text='Unique identifier for the observing network in the ROPO database.',
        default=uuid.uuid4
    )
   
    
    # Network scope and coverage
    domains = ParentalManyToManyField(
        Domain,
        verbose_name='Domains',
        help_text='Scope of observations across Atmosphere, Land, and/or Ocean.'
    )
    disciplines = ParentalManyToManyField(
        Discipline,
        verbose_name='Disciplines',
        help_text='Branch of scientific knowledge or thematic focus for the observing network.'
    )
    regions = ParentalManyToManyField(
        Region,
        verbose_name='Regions',
        help_text='Spatial coverage of the network as described by one or more broad geographical areas, such as Arctic, Antarctica, Southern Ocean, etc.'
    )
    subregions = ParentalManyToManyField(
        Subregion,
        verbose_name='Subregions',
        help_text='Spatial coverage of the network as described by smaller geographic areas, such as Alaska, Iceland, Beaufort Sea, Russian Subarctic, West Antarctica, Ross Sea, etc.'
    )

    # Spatial data
    geometry_field = StreamField(
        [
            ('bounding_box', SOSOBoundingBoxBlock(label='Bounding Box')),
        ],
        verbose_name='Spatial Extent',
        help_text='Spatial coverage of the network as delineated by one or more bounding boxes. Each box is defined as a pair of latitude and longitude coordinates for the southwest and northeast corners.'
    )
    start_year = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        verbose_name='Year Started', 
        help_text='The year that observations within the network began.',
        validators=[validate_start_year]
    )
    contact = models.CharField(
        max_length=255,
        verbose_name='Contact',
        help_text='Email address or URL for contacting the observing network.',
        validators=[validate_email_or_url]
    )
    data_repository_url = StreamField(
        [
            ('url', blocks.URLBlock(label='Data Repository URL')),
        ],
        blank=True,
        null=True,
        verbose_name='Data Repository',
        help_text='One or more links to data repositories hosting scientific data from the network (such as the Polar Data Catalogue, NSF Arctic Data Center, or PANGAEA).  (This field pertains to scientific datasets, not observing assets).'
    )
    network_id = StreamField(
        [
            ('network_id', NetworkIdBlock(label='Network ID')),
        ],
        blank=True,
        null=True,
        verbose_name='Network IDs',
        help_text='An identifier for the network generated by an organization, registry, or catalog (Text or URL). e.g. network identifiers from ROR, DEIMS-SDR, RRID, Zenodo Communities, NOAA EORES, etc.'
    )
    asset_types = ParentalManyToManyField(
        AssetType,
        blank=True,
        verbose_name='Asset Types',
        help_text='Categorization of discrete infrastructure or coordinated activities for observing such as sites, mobile platforms, projects, campaigns, and initiatives.'
    )
    has_catalog = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
            ('under_development', 'Under Development')
        ],
        verbose_name='Asset Metadata Catalog',
        help_text='Does the network have a catalog, spreadsheet, list, or other means of tracking details about individual observing assets such as observing sites, mobile platforms, research projects, field campaigns, cruises, programs, etc.?  (This field pertains to observing assets, not scientific datasets). ',
    )
    metadata_access = models.CharField(
        max_length=20,
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
            ('under_development', 'Under Development')
        ],
        blank=True,
        null=True,
        verbose_name='Metadata Access',
        help_text="Is the network's asset-level catalog, spreadsheet, list, or other documentation enabled online for public viewing, download, or other access? If partially enabled, select Yes."
    )
    machine_readable = models.CharField(
        max_length=20,
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
            ('under_development', 'Under Development')
        ],
        blank=True,
        null=True,
        verbose_name='Machine Readable Access',
        help_text="Is the network's asset-level metadata catalog enabled for access with an API or endpoint URL for automated harvesting of asset-level metadata records? If partially enabled, select Yes."
    )
    metadata_standards = ParentalManyToManyField(
        MetadataStandard,
        blank=True,
        verbose_name='Metadata Standards',
        help_text="Metadata standards, or a custom schema, in use for public access to a network's structured information about observing assets (such as ISO 19115, INSPIRE EF, WMO WIGOS, etc.)."
    )
    access_protocols = ParentalManyToManyField(
        AccessProtocol,
        blank=True,
        verbose_name='Access Protocols',
        help_text="Transfer protocols or web service formats in use for public access to a network's structured information about observing assets (such as file download, custom API, OGC WMS, or OAI-PMH)."
    )
    metadata_catalog_url = StreamField(
        [
            ('url', blocks.URLBlock(label='Metadata Catalog URL')),
        ],
        blank=True,
        null=True,
        verbose_name='Metadata Catalog Links',
        help_text="Link to one or more webpages presenting a network's catalog, spreadsheet, list, or other documentation about observing assets."
    )
    
    class Meta:
        verbose_name = 'Observing Network'

        
    @property
    @admin.display(description='Last Modified By')
    def last_modified_by(self):
        return self.latest_revision.user

    @property
    @admin.display(description='Date Last Modified')
    def date_last_modified(self):
        return self.latest_revision_created_at

    def clean(self):
        """
        Validate the model fields, including logo URL validation.
        
        This method validates that the logo_url (if provided) can be successfully
        downloaded before the page is saved. This ensures validation errors are
        properly displayed in the admin form rather than causing exception pages.
        
        Raises:
            ValidationError: If any field validation fails, including logo download issues.
        """
        super().clean()
        
        # Validate logo URL by attempting to access it if URL is provided and should be validated
        if self.logo_url and self._should_validate_logo_url():
            try:
                validate_image_url(self.logo_url, timeout=5)
            except ValidationError as e:
                # Re-raise with logo_url field targeting for proper form display
                raise ValidationError({'logo_url': e.message})

    def _should_validate_logo_url(self):
        """
        Determine if we should validate the logo URL.
        
        We validate when:
        1. There's no existing logo image, OR
        2. The logo_url field has changed from its original value
        
        Returns:
            bool: True if logo URL should be validated, False otherwise.
        """
        # If no logo image exists, we should validate
        if not self.logo_image:
            return True
            
        # Check if logo_url field has changed from database value
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                return original.logo_url != self.logo_url
            except self.__class__.DoesNotExist:
                return True
        
        # For new objects, always validate if URL is provided
        return True

    # @transaction.atomic
    def save(self, *args, **kwargs):
        # Ensure that the observing network page is not a child of another observing network page
        self.name = self.title
           
        # Download logo image if validation passed and conditions are met
        # This happens after clean() validation has passed
        if self.logo_url and self._should_download_logo(**kwargs):
            self._download_logo_image()

        result = super().save(*args, **kwargs)
        return result

    def _should_download_logo(self, **kwargs):
        """
        Determine if we should download the logo image.
        
        We download when:
        1. There's no existing logo image, OR
        2. The logo_url field has changed, OR  
        3. We're in a publishing scenario where live_revision_id matches latest_revision_id
        
        Args:
            **kwargs: Additional keyword arguments from save method
            
        Returns:
            bool: True if logo should be downloaded, False otherwise.
        """
        # Always download if no logo image exists
        if not self.logo_image:
            return True
            
        # Check if logo_url field has changed
        if self._has_field_changed('logo_url', **kwargs):
            return True
            
        # Download during publishing (when live and latest revisions match)
        if self.live_revision_id and self.latest_revision_id and self.live_revision_id == self.latest_revision_id:
            return True
            
        return False

    def _download_logo_image(self):
        """
        Download and save the logo image from the URL.
        
        This method performs the actual download and creates the Image object.
        It should only be called after URL validation has passed in clean().
        """
        try:
            if settings.DEBUG:
                print(f"Downloading logo from {self.logo_url}")
                
            response = requests.get(self.logo_url, timeout=10)  # Longer timeout for actual download
            response.raise_for_status()

            # Get filename from URL
            img_name = os.path.basename(self.logo_url)
            img_file_name = f"{self.pk}-{self.abbreviation}-{img_name}"
            
            # Create a new image object
            image = Image(
                title=f"{self.name} Logo", 
                file=ImageFile(BytesIO(response.content), name=img_file_name),
                uploaded_by_user=self.owner
            )
            image._set_image_file_metadata()
            image.save()
            self.logo_image = image
            
            if settings.DEBUG:
                print(f"Successfully downloaded and saved logo for {self.name}")
                
        except Exception as e:
            # Log the error but don't raise - validation should have caught issues
            if settings.DEBUG:
                print(f"Error downloading logo (should have been caught in validation): {str(e)}")
            # Optionally, we could still raise here if we want to be extra safe
            # raise ValidationError({'logo_url': f"Failed to download logo: {str(e)}"}) 

    def _has_field_changed(self, field_name, **kwargs):
        """
        Check if a field has changed from its database value.
        
        Args:
            field_name (str): Name of the field to check
            **kwargs: Additional keyword arguments (unused but kept for compatibility)
            
        Returns:
            bool: True if field has changed or object is new, False otherwise
        """
        if self.pk is None:
            return True
            
        try:
            # Get the current object from database
            current_obj = self.__class__.objects.get(pk=self.pk)  
            # Compare the current field value with the database value
            current_value = getattr(current_obj, field_name)
            new_value = getattr(self, field_name)
            return new_value != current_value
        except self.__class__.DoesNotExist:
            return True

    promote_panels = []

    content_panels =  [
        HelpPanel(
            classname='on-help-panel',
            heading='Welcome to the "Add Observing Network" Page!',
            content=get_observing_network_help_content()
        ),

        # Network Information (following metadata model sequence)
        # FieldPanel('name'),
        FieldPanel('title',
                   heading='Network Name',
                   help_text='The full name of the observing network e.g. Svalbard Integrated Arctic Earth Observing System.'),
        FieldPanel('abbreviation'),
        FieldPanel('description'),
        FieldPanel('website_url'),
        FieldPanel('logo_url'),
        MultipleChooserPanel('network_organizations',
                             chooser_field_name='organization',
                             heading='Organizations',
                             label="Organization",
                             panels=None
                         ),
        FieldPanel('contact'),
        FieldPanel('data_repository_url'),
        FieldPanel('network_id'),

        # Observational Scope
        MultiFieldPanel([
            FieldPanel('domains', widget=forms.CheckboxSelectMultiple),
            FieldPanel('disciplines', widget=forms.CheckboxSelectMultiple),
        ], heading="Observational Scope"),

        # Spatial and Temporal Coverage
        MultiFieldPanel([
            FieldPanel('start_year'),
            FieldPanel('regions', widget=forms.CheckboxSelectMultiple),
            FieldPanel('subregions', widget=forms.CheckboxSelectMultiple),
            FieldPanel('geometry_field'),
        ], heading="Spatial and Temporal Coverage"),

        # Observing Assets and Asset-Level Metadata Interoperability
        MultiFieldPanel([
            FieldPanel('asset_types', widget=forms.CheckboxSelectMultiple),
            FieldPanel('has_catalog'),
            FieldPanel('metadata_access'),
            FieldPanel('machine_readable'),
            FieldPanel('metadata_standards', widget=forms.CheckboxSelectMultiple),
            FieldPanel('access_protocols', widget=forms.CheckboxSelectMultiple),
            FieldPanel('metadata_catalog_url'),
        ], heading="Observing Assets"),

    ]

    admin_panel = [
        FieldPanel('owner', help_text='The user who is responsible for this Observing Network',permission='ropon_data.change_owner_observingnetworkpage'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),  
        ObjectList(admin_panel, heading='Admin area', ),
    ])

    api_fields = [
        APIField('name'),
        APIField('abbreviation'),
        APIField('description'),
        APIField('website_url'),
        APIField('logo_url'),
        APIField('logo_image'),
        APIField('ropon_id'),
        APIField('organization_name', serializers.StringRelatedField(many=True, read_only=True, source = "network_organizations"),),
        APIField('domains',serializers.StringRelatedField(many=True, read_only=True)),
        APIField('disciplines',serializers.StringRelatedField(many=True, read_only=True)), 
        APIField('regions',serializers.StringRelatedField(many=True, read_only=True)),
        APIField('subregions',serializers.StringRelatedField(many=True, read_only=True)),
        APIField('geometry_field'),
        APIField('start_year'),
        APIField('contact'),
        APIField('data_repository_url'),
        APIField('network_id'),
        APIField('asset_types',serializers.StringRelatedField(many=True, read_only=True)),
        APIField('has_catalog',serializers.CharField(source='get_has_catalog_display',read_only=True)),
        APIField('metadata_access',serializers.CharField(source='get_metadata_access_display',read_only=True)),
        APIField('machine_readable',serializers.CharField(source='get_machine_readable_display',read_only=True)),
        APIField('metadata_standards',serializers.StringRelatedField(many=True, read_only=True)),
        APIField('access_protocols',serializers.StringRelatedField(many=True, read_only=True)),
        APIField('metadata_catalog_url'),

    ]

    # api_meta_fields = ["detail_url",
    #                    "slug",
    #                    "first_published_at",
    #                    "date_last_modified",
    #                    "alias_of"
    # ]
    search_fields = Page.search_fields + [
        index.SearchField('name'),
        index.SearchField('description'),
        index.SearchField('abbreviation'),

    ]

    # diable preview for Observing Network Page
    def is_previewable(self):
        if flag_enabled(FLAG_REMOVE_PREVIEW_OPTIONS):
            return False
        return super().is_previewable()
    
    def __str__(self):
        return self.name

    @admin.display(description='Status')
    def status(self):
        status = self.status_string or ''
        return status.upper()

    @classmethod
    def get_openapi_schema(cls) -> dict:
        """
        Generate OpenAPI schema for API response.

        Combines:
        - Auto-introspected Django fields
        - Block schemas from StreamField blocks
        - Manual definitions for M2M and Wagtail-specific fields
        """
        from ropon_data.blocks import (
            SOSOBoundingBoxBlock, NetworkIdBlock, get_url_block_schema
        )

        properties = {}

        # Auto-generate basic field schemas from model fields
        for field in cls._meta.get_fields():
            field_name = field.name

            # Skip Wagtail internal fields and non-relevant fields
            if field_name in ['page_ptr', 'title','path', 'depth', 'numchild',
                              'content_type', 'live', 'has_unpublished_changes',
                              'url_path', 'owner', 'go_live_at', 'expire_at',
                              'expired', 'locked', 'locked_at', 'locked_by',
                              'first_published_at', 'last_published_at',
                              'live_revision', 'alias_of', 'latest_revision',
                              'translation_key', 'locale', 'slug', 'seo_title',
                              'show_in_menus', 'search_description', 'draft_title',
                              'observingnetworkindexpage', 'revision', 'workflow_states',
                              'aliases', 'revisions', 'subscribers', 'comments',
                              'sites_rooted_here', 'aliases_of_me', 'sites_rooted_here',
                              'group_permissions', 'view_restrictions', 'is_owner_authorized',
                              'logo_image']:
                continue

            # Skip StreamFields (handled separately with block schemas)
            if hasattr(field, 'stream_block'):
                continue

            # Handle M2M fields (API serializes as string arrays via StringRelatedField)
            if field.many_to_many:
                properties[field_name] = {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': str(field.help_text) if hasattr(field, 'help_text') and field.help_text else f'{field.verbose_name} values.'
                }
                continue

            # Skip other relation fields (ForeignKey, reverse relations - handled separately)
            if field.is_relation:
                continue

            # Generate schema for basic fields
            properties[field_name] = cls._field_to_schema(field)

        # Add StreamField schemas from block classes
        # properties['geometry_field'] = {
        #     'type': 'array',
        #     'items': SOSOBoundingBoxBlock.get_openapi_schema(include_streamfield_wrapper=True),
        #     'description': 'Spatial coverage of the network as delineated by one or more bounding boxes. Each box is defined as a pair of latitude and longitude coordinates for the southwest and northeast corners.Spatial coverage of the network as delineated by one or more bounding boxes. Each box is defined as a pair of latitude and longitude coordinates for the southwest and northeast corners.'
        # }
        properties['geometry_field'] = {
            'type': 'array',
            '$ref': '#/components/schemas/SOSOBoundingBox',
            'description': 'Spatial coverage of the network as delineated by one or more bounding boxes. Each box is defined as a pair of latitude and longitude coordinates for the southwest and northeast corners.Spatial coverage of the network as delineated by one or more bounding boxes. Each box is defined as a pair of latitude and longitude coordinates for the southwest and northeast corners.'
        }
        properties['data_repository_url'] = {
            'type': 'array',
            'items': get_url_block_schema('url'),
            'description': 'One or more links to data repositories hosting scientific data from the network (such as the Polar Data Catalogue, NSF Arctic Data Center, or PANGAEA).  (This field pertains to scientific datasets, not observing assets).'
        }
        properties['metadata_catalog_url'] = {
            'type': 'array',
            'items': get_url_block_schema('url'),
            'description': "Link to one or more webpages presenting a network's catalog, spreadsheet, list, or other documentation about observing assets."
        }
        properties['network_id'] = {
            'type': 'array',
            'items': NetworkIdBlock.get_openapi_schema(),
            'description': 'An identifier for the network generated by an organization, registry, or catalog (Text or URL). e.g. network identifiers from ROR, DEIMS-SDR, RRID, Zenodo Communities, NOAA EORES, etc.'
        }

        # Special case: organization_name uses a different source (network_organizations reverse relation)
        properties['organization_name'] = {
            'type': 'array',
            'items': {'type': 'string'},
            'description': 'Organizations associated with this network.'
        }

        # Wagtail-specific nested objects
        properties['id'] = {'type': 'integer', 'description': 'Page ID.'}
        properties['meta'] = {'$ref': '#/components/schemas/ObservingNetworkMeta'}
        # properties['logo_image'] = {'$ref': '#/components/schemas/LogoImage'}

        return {
            'type': 'object',
            'description': 'Observing Network registered in RoPON.',
            'properties': properties
        }

    @staticmethod
    def _field_to_schema(field) -> dict:
        """Map Django field to OpenAPI schema."""
        from django.db import models as django_models
        from wagtail.fields import StreamField

        type_map = {
            django_models.CharField: {'type': 'string'},
            django_models.TextField: {'type': 'string'},
            django_models.IntegerField: {'type': 'integer'},
            django_models.URLField: {'type': 'string', 'format': 'uri'},
            django_models.UUIDField: {'type': 'string', 'format': 'uuid'},
            django_models.DateTimeField: {'type': 'string', 'format': 'date-time'},
            django_models.BooleanField: {'type': 'boolean'},
        }

        # Handle choice fields -> enum
        if hasattr(field, 'choices') and field.choices:
            return {
                'type': 'string',
                'enum': [c[1] for c in field.choices],
                'description': str(field.help_text) if hasattr(field, 'help_text') and field.help_text else None
            }

        # Map field type
        for field_class, schema in type_map.items():
            if isinstance(field, field_class):
                result = schema.copy()
                if hasattr(field, 'max_length') and field.max_length:
                    result['maxLength'] = field.max_length
                if hasattr(field, 'null') and field.null:
                    result['nullable'] = True
                if hasattr(field, 'help_text') and field.help_text:
                    result['description'] = str(field.help_text)
                return result

        return {'type': 'string'}

    class Meta:
        verbose_name = 'Observing Network'
        permissions = [
            ('publish_observingnetworkpage', 'Can publish observing network page'),
            ('change_owner_observingnetworkpage', 'Can change owner of Observing Network')
        ]

    # Allow ObservingNetworkPage to be created at the root level
    parent_page_types = ['ObservingNetworkIndexPage']
    subpage_types = []


# Observing Network Index Page which will contain Observing Network Pages
class ObservingNetworkIndexPage( Page):
    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    # Allow ObservingNetworkIndexPage to be created at the root level
    # parent_page_types = ['wagtailcore.Page']
    subpage_types = ['ObservingNetworkPage']

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
    ]

    class Meta:
        verbose_name = 'Observing Networks Page'
