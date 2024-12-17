# ropon_data/models.py

from django.db import models
from django.contrib.auth import get_user_model
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.models import RevisionMixin, WorkflowMixin, DraftStateMixin
from modelcluster.fields import ParentalManyToManyField
from wagtail.search import index
from django import forms
from django.core import validators

User = get_user_model()

# Controlled Vocabulary Models
# ropon_data/models.py

class ControlledVocabularyModel(models.Model):
    """Base class for all controlled vocabulary models"""
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    panels = [FieldPanel('name')]

    def __str__(self):
        return self.name

# Update controlled vocabulary models to inherit from base class
class Domain(ControlledVocabularyModel):
    pass

class Discipline(ControlledVocabularyModel):
    pass

class Region(ControlledVocabularyModel):
    pass

class AssetType(ControlledVocabularyModel):
    pass

class MetadataStandard(ControlledVocabularyModel):
    pass

class AccessProtocol(ControlledVocabularyModel):
    pass

# Subregion is special as it has a relation
class Subregion(ControlledVocabularyModel):
    pass




# ObservingNetwork Model

class ObservingNetwork( WorkflowMixin,DraftStateMixin, RevisionMixin, models.Model):
    name = models.CharField(max_length=255,verbose_name='Network Name',help_text='The full name of the observing network e.g. Svalbard Integrated Arctic Earth Observing System')
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='observing_networks'
    )
    abbreviation = models.CharField(max_length=255, verbose_name='Network Abbreviation', help_text='Acronym or short name of the observing network. e.g. SIOS')
    description = models.TextField(verbose_name='Network Description', help_text='Short summary of the observing network, including geographic or thematic scope.')
    website_url = models.URLField(verbose_name='Network Website', help_text='URL to the observing network website')
    logo_url = models.URLField(verbose_name='Network Logo', help_text='URL to the observing network logo')
    ropon_id = models.CharField(max_length=255, unique=True)
    organization_name = models.CharField(max_length=255, verbose_name='Organization Name', help_text='One or more entities responsible for funding or operation of the observing network.')
    domains = ParentalManyToManyField(Domain, verbose_name='Domains', help_text='Scope of observations across Atmosphere, Land, and/or Ocean.')
    disciplines = ParentalManyToManyField(Discipline, verbose_name='Disciplines', help_text='Branch of scientific knowledge or thematic focus for the observing network.')
    regions = ParentalManyToManyField(Region, verbose_name='Regions', help_text='Spatial coverage of the network as described by one or more broad geographical areas, such as Arctic, Antarctica, Southern Ocean, etc.')
    subregions = ParentalManyToManyField(Subregion, verbose_name='Subregions', help_text='Spatial coverage of the network as described by smaller geographic areas, such as Alaska, Iceland, Beaufort Sea, Russian Subarctic, West Antarctica, Ross Sea, etc.')
    geometry = models.TextField(verbose_name='Spatial Extent', help_text='Spatial coverage of the network as delineated by one or more polygons, each as a series of four or more points in latitude and longitude (decimal degrees), where the first and final points are identical (e.g., "polygon": "67.6199 -42.3773 67.6199 17.1685 57.7191 17.1685 57.7191 -42.3773 67.6199 -42.3773").  Separate polygons with the pipe ("|") symbol.')
    start_year = models.PositiveIntegerField(blank=True, null=True, verbose_name='Year Started', help_text='The year that observations within the network began.')
    contact = models.CharField(
        max_length=255,
        verbose_name='Contact',
        help_text='Email address or URL for contacting the observing network.',
        validators=[
            validators.EmailValidator(message="Enter a valid email address."),
            validators.URLValidator(message="Enter a valid URL.")
        ]
    )
    data_repository_url = models.URLField(blank=True, null=True, verbose_name='Data Repository', help_text='One or more links to data repositories hosting scientific data from the network (such as the Polar Data Catalogue, NSF Arctic Data Center, or PANGAEA).  (This field pertains to scientific datasets, not observing assets).')
    asset_types = ParentalManyToManyField(AssetType, verbose_name='Asset Types', help_text='Categorization of discrete infrastructure or coordinated activities for observing such as sites, mobile platforms, projects, campaigns, and initiatives.')
    has_catalog = models.CharField(
        max_length=20,
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
    metadata_catalog_url = models.URLField(blank=True, null=True, verbose_name='Metadata Catalog Links', help_text="Link to one or more webpages presenting a network's catalog, spreadsheet, list, or other documentation about observing assets.")
    date_last_modified = models.DateField(auto_now=True)
    last_modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_observing_networks'
    )

    panels = [
        FieldPanel('name'),
        # FieldPanel('owner'),
        FieldPanel('abbreviation'),
        FieldPanel('description'),
        FieldPanel('website_url'),
        FieldPanel('logo_url'),
        # FieldPanel('ropon_id'),
        FieldPanel('organization_name'),
        MultiFieldPanel([
            FieldPanel('domains', widget=forms.CheckboxSelectMultiple),
            FieldPanel('disciplines', widget=forms.CheckboxSelectMultiple),
        ], heading="Observational Scope"),
        MultiFieldPanel([   
             FieldPanel('regions', widget=forms.CheckboxSelectMultiple),
            FieldPanel('subregions', widget=forms.CheckboxSelectMultiple),
            FieldPanel('geometry'),
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

    search_fields = [
        index.SearchField('name'),
        index.SearchField('description'),
        index.SearchField('organization_name'),
    ]

    def __str__(self):
        return self.name
