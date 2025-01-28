# ropon_data/models.py

from django.db import models
from django.contrib.auth import get_user_model
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail.models import  Page
from modelcluster.fields import ParentalManyToManyField
from wagtail.search import index
from wagtail.fields import StreamField
from wagtail import blocks
from django import forms
from wagtail.api import APIField


from ropon_data.blocks import SOSOBoundingBoxBlock
from .validators import (
    validate_email_or_url,
    validate_start_year
)
from django.utils.html import format_html
import uuid
from django.contrib import admin
from wagtail.models import Page

from rest_framework import serializers

User = get_user_model()

# ------ Controlled Vocabulary Models --------


# Base class for all controlled vocabulary models
class ControlledVocabularyModel(models.Model):
    """Base class for all controlled vocabulary models"""
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    panels = [FieldPanel('name')]

    def __str__(self):
        return self.name
    
    api_fields = [
        APIField('name'),
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


# ------ Observing Network Page Models --------

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
        verbose_name='Network Logo',
        help_text='URL to the observing network logo'
    )
    ropon_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='ROPON ID',
        help_text='Unique identifier for the observing network in the ROPO database.',
        default=uuid.uuid4
    )
    organization_name = models.CharField(
        max_length=255,
        verbose_name='Organization Name',
        help_text='One or more entities responsible for funding or operation of the observing network.'
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
    asset_types = ParentalManyToManyField(AssetType, verbose_name='Asset Types', help_text='Categorization of discrete infrastructure or coordinated activities for observing such as sites, mobile platforms, projects, campaigns, and initiatives.')
    has_catalog = models.CharField(
        max_length=20,
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
            ('under_development', 'Under Development')
        ],
        verbose_name='Asset Metadata Catalog',
        help_text='Does the network has a catalog, spreadsheet, list, or other means of tracking details about individual observing assets such as observing sites, mobile platforms, research projects, field campaigns, cruises, programs, etc.?  (This field pertains to observing assets, not scientific datasets). ',
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
        help_text="Is the network's asset-level catalog, spreadsheet, list, or other documentation enabled online for public viewing, download, or other access?"
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
        help_text="Is the network's asset-level metadata catalog enabled for access with an API or endpoint URL for automated harvesting of asset-level metadata records?"
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
        return self.latest_revision_user

    @property
    @admin.display(description='Date Last Modified')
    def date_last_modified(self):
        return self.latest_revision_created_at

    def save(self, *args, **kwargs):
        # Ensure that the observing network page is not a child of another observing network page
        self.title = self.name
        super().save(*args, **kwargs)

    promote_panels = []

    content_panels =  [
        FieldPanel('name'),
        FieldPanel('abbreviation'),
        FieldPanel('description'),
        FieldPanel('website_url'),
        FieldPanel('logo_url'),
        FieldPanel('organization_name'),
        MultiFieldPanel([
            FieldPanel('domains', widget=forms.CheckboxSelectMultiple),
            FieldPanel('disciplines', widget=forms.CheckboxSelectMultiple),
        ], heading="Observational Scope"),
        MultiFieldPanel([
            FieldPanel('regions', widget=forms.CheckboxSelectMultiple),
            FieldPanel('subregions', widget=forms.CheckboxSelectMultiple),
            FieldPanel('geometry_field'),
            FieldPanel('start_year'),
        ], heading="Spatial and Temporal Coverage"),
        FieldPanel('contact'),
        FieldPanel('data_repository_url'),
        MultiFieldPanel([
            FieldPanel('asset_types', widget=forms.CheckboxSelectMultiple),
            FieldPanel('has_catalog'),
            FieldPanel('metadata_access'),
            FieldPanel('machine_readable'),
            FieldPanel('metadata_standards', widget=forms.CheckboxSelectMultiple),
            FieldPanel('access_protocols', widget=forms.CheckboxSelectMultiple),
            FieldPanel('metadata_catalog_url'),
        ], heading="Metadata Access"),
    ]

    admin_panel = [
        FieldPanel('owner', help_text='The user who is responsible for this Observing Network'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),  
        ObjectList(admin_panel, heading='Admin area', permission='ropon_data.change_owner_observingnetworkpage'),
    ])

    api_fields = [
        APIField('name'),
        APIField('abbreviation'),
        APIField('description'),
        APIField('website_url'),
        APIField('logo_url'),
        APIField('ropon_id'),
        APIField('organization_name'),
        APIField('domains',serializers.StringRelatedField(many=True, read_only=True)),
        APIField('disciplines',serializers.StringRelatedField(many=True, read_only=True)), 
        APIField('regions',serializers.StringRelatedField(many=True, read_only=True)),
        APIField('subregions',serializers.StringRelatedField(many=True, read_only=True)),
        APIField('geometry_field'),
        APIField('start_year'),
        APIField('contact'),
        APIField('data_repository_url'),
        APIField('asset_types',serializers.StringRelatedField(many=True, read_only=True)),
        APIField('has_catalog'),
        APIField('metadata_access'),
        APIField('machine_readable'),
        APIField('metadata_standards',serializers.StringRelatedField(many=True, read_only=True)),
        APIField('access_protocols',serializers.StringRelatedField(many=True, read_only=True)),
        APIField('metadata_catalog_url'),

    ]
    search_fields = Page.search_fields + [
        index.SearchField('name'),
        index.SearchField('description'),
        index.SearchField('organization_name'),
    ]

    def __str__(self):
        return self.name

    @admin.display(description='Status')
    def status(self):
        status = self.status_string or ''
        return status.upper()

    class Meta:
        verbose_name = 'Observing Network'
        permissions = [
            ('publish_observingnetworkpage', 'Can publish observing network page'),
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
