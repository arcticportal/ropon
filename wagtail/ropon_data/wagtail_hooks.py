
# ropon_data/wagtail_hooks.py

from django.urls import reverse
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.admin.menu import MenuItem
from wagtail.snippets.models import register_snippet
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

# class ObservingNetworkViewSet(SnippetViewSet):
#     model = ObservingNetwork
#     menu_label = 'Observing Networks'
#     menu_name = 'bbserving_networks'
#     menu_icon = 'site'
#     list_display = ('abbreviation','name', 'owner', 'status')
#     search_fields = ('name', 'description', 'organization_name')
#     menu_order = 100  # Adjust the order as needed
#     add_to_admin_menu= True

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


class ObservingNetworkPageViewSet(PageListingViewSet):
    model = ObservingNetworkPage
    menu_label = 'Observing Networks'
    menu_name = 'observing_network_pages'
    menu_icon = 'doc-full'
    list_display = ('name', 'owner', 'status', 'last_modified_by')
    search_fields = ('name', 'description', 'organization_name')
    menu_order = 150  # Adjust the order as needed
    add_to_admin_menu = True

@hooks.register('register_admin_viewset')
def register_observing_network_page_viewset():
    return ObservingNetworkPageViewSet("observing_networks")
