
# ropon_data/wagtail_hooks.py

from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup
from .models import (
    ObservingNetwork, Domain, Discipline, Region,
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

class AccessProtocolViewSet(ControlledVocabularyViewSet):
    model = AccessProtocol

class SubregionViewSet(SnippetViewSet):
    model = Subregion
    menu_icon = 'list-ul'
    list_display = ('name', 'region')
    search_fields = ('name', 'region__name')

class ObservingNetworkViewSet(SnippetViewSet):
    model = ObservingNetwork
    menu_label = 'Observing Networks'
    menu_icon = 'site'
    list_display = ('title', 'owner', 'network_abbreviation')
    search_fields = ('title', 'network_description', 'organization')

# Group controlled vocabulary snippets
class ControlledVocabularyGroup(SnippetViewSetGroup):
    menu_label = 'Controlled Vocabulary'
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
register_snippet(ObservingNetworkViewSet)


