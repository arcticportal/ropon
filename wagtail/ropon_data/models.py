# ropon_data/models.py

from django.db import models
from django.contrib.auth import get_user_model
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.models import RevisionMixin, WorkflowMixin
from modelcluster.fields import ParentalManyToManyField
from wagtail.search import index
from django import forms

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
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='subregions'
    )

    panels = [FieldPanel('region'), FieldPanel('name')]

    def __str__(self):
        return f"{self.region.name} - {self.name}"






# ObservingNetwork Model

class ObservingNetwork(RevisionMixin, WorkflowMixin, models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='observing_networks'
    )
    network_abbreviation = models.CharField(max_length=255)
    network_description = models.TextField()
    network_website = models.URLField()
    network_logo = models.ImageField(upload_to='network_logos/', blank=True, null=True)
    network_ropon_id = models.CharField(max_length=255, unique=True)
    organization = models.CharField(max_length=255, blank=True, null=True)
    domains = ParentalManyToManyField(Domain, blank=True)
    disciplines = ParentalManyToManyField(Discipline, blank=True)
    regions = ParentalManyToManyField(Region, blank=True)
    subregions = ParentalManyToManyField(Subregion, blank=True)
    spatial_extent = models.TextField(blank=True, null=True)
    year_started = models.PositiveIntegerField(blank=True, null=True)
    contact = models.CharField(max_length=255)
    data_repository = models.URLField(blank=True, null=True)
    asset_types = ParentalManyToManyField(AssetType, blank=True)
    asset_metadata_catalog = models.CharField(
        max_length=20,
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
            ('under_development', 'Under Development')
        ]
    )
    metadata_access = models.CharField(
        max_length=20,
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
            ('under_development', 'Under Development')
        ],
        blank=True,
        null=True
    )
    machine_readable_access = models.CharField(
        max_length=20,
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
            ('under_development', 'Under Development')
        ],
        blank=True,
        null=True
    )
    metadata_standards = ParentalManyToManyField(MetadataStandard, blank=True)
    access_protocols = ParentalManyToManyField(AccessProtocol, blank=True)
    metadata_catalog_links = models.URLField(blank=True, null=True)
    date_last_modified = models.DateField(auto_now=True)
    last_modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_observing_networks'
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('owner'),
        FieldPanel('network_abbreviation'),
        FieldPanel('network_description'),
        FieldPanel('network_website'),
        FieldPanel('network_logo'),
        FieldPanel('network_ropon_id'),
        FieldPanel('organization'),
        MultiFieldPanel([
            FieldPanel('domains', widget=forms.CheckboxSelectMultiple),
            FieldPanel('disciplines', widget=forms.CheckboxSelectMultiple),
            FieldPanel('regions', widget=forms.CheckboxSelectMultiple),
            FieldPanel('subregions', widget=forms.CheckboxSelectMultiple),
        ], heading="Observational Scope"),
        FieldPanel('spatial_extent'),
        FieldPanel('year_started'),
        FieldPanel('contact'),
        FieldPanel('data_repository'),
        FieldPanel('asset_types', widget=forms.CheckboxSelectMultiple),
        MultiFieldPanel([
            FieldPanel('asset_metadata_catalog'),
            FieldPanel('metadata_access'),
            FieldPanel('machine_readable_access'),
        ], heading="Metadata Access"),
        FieldPanel('metadata_standards', widget=forms.CheckboxSelectMultiple),
        FieldPanel('access_protocols', widget=forms.CheckboxSelectMultiple),
        FieldPanel('metadata_catalog_links'),
    ]

    search_fields = [
        index.SearchField('title'),
        index.SearchField('network_description'),
        index.SearchField('organization'),
    ]

    def __str__(self):
        return self.title
