
# ropon_data/wagtail_hooks.py

from django.urls import reverse
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.admin.menu import MenuItem
from wagtail.snippets.models import register_snippet
from wagtail.admin.ui.tables import Column, DateColumn

from wagtail.admin.ui.tables.pages import BulkActionsColumn, PageTitleColumn, PageStatusColumn
from wagtail import hooks


from .models import (
     Domain, Discipline, ObservingNetworkPage, Region,
    Subregion, AssetType, MetadataStandard, AccessProtocol
)

# Define custom SnippetViewSet classes


class ControlledVocabularyViewSet(SnippetViewSet):
    """Base viewset for controlled vocabulary models"""
    menu_icon = 'list-ul'
    list_display = ('name',)
    search_fields = ('name',)

class DomainViewSet(ControlledVocabularyViewSet):
    model = Domain

class DisciplineViewSet(ControlledVocabularyViewSet):
    model = Discipline

class RegionViewSet(ControlledVocabularyViewSet):
    model = Region

class AssetTypeViewSet(ControlledVocabularyViewSet):
    model = AssetType

class MetadataStandardViewSet(ControlledVocabularyViewSet):
    model = MetadataStandard
    list_display = ('name', 'source_url_link')
    search_fields = ('name', 'description')

class AccessProtocolViewSet(ControlledVocabularyViewSet):
    model = AccessProtocol
    list_display = ('name', 'source_url_link')
    search_fields = ('name', 'description')

class SubregionViewSet(ControlledVocabularyViewSet):
    model = Subregion

# Group controlled vocabulary snippets
class ControlledVocabularyGroup(SnippetViewSetGroup):
    menu_label = 'Controlled Vocabulary'
    menu_name = 'controlled_vocabulary'
    menu_icon = 'tag'
    menu_order = 200
    items = (
        DomainViewSet,
        DisciplineViewSet,
        RegionViewSet,
        SubregionViewSet,
        AssetTypeViewSet,
        MetadataStandardViewSet,
        AccessProtocolViewSet,
    )

# Register the group and ObservingNetwork separately
register_snippet(ControlledVocabularyGroup)
# register_snippet(ObservingNetworkViewSet)



class ObservingNetworkFilterSet(PageListingViewSet.filterset_class):
    class Meta:
        model = ObservingNetworkPage
        fields = [
                  "organization_name",
                  ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove unwanted fields
        self.filters.pop("site", None)
        self.filters.pop("has_child_pages", None)

class ObservingNetworkPageViewSet(PageListingViewSet):
    model = ObservingNetworkPage
    menu_label = 'Observing Networks'
    menu_name = 'observing_network_pages'
    menu_icon = 'doc-full'
    # list_display = ('name', 'organization_name', 'owner', 'last_modified_by')
    columns =  [
        BulkActionsColumn("bulk_actions"),
        PageTitleColumn('name', label='Name', classname='name'),
        Column('organization_name', label='Organization', classname='organization_name',sort_key='organization_name'),
        PageStatusColumn('status', label='Status', classname='status', sort_key='live'),
        DateColumn('date_last_modified', label='Last Updated', classname='date_last_modified'),
        ]
    filterset_class = ObservingNetworkFilterSet
    search_fields = ('name', 'description', 'organization_name')
    menu_order = 150  # Adjust the order as needed
    add_to_admin_menu = True

@hooks.register('register_admin_viewset')
def register_observing_network_page_viewset():
    return ObservingNetworkPageViewSet("observing_networks")
