
# Define custom SnippetViewSet classes
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup



from ropon_data.models import (
     Domain, Discipline,  Region,
    Subregion, AssetType, MetadataStandard,
    AccessProtocol
)

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
