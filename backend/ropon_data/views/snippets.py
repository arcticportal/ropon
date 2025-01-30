
# Define custom SnippetViewSet classes
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup



from ropon_data.models import (
     Domain, Discipline,  Region,
    Subregion, AssetType, MetadataStandard,
    AccessProtocol, Organization
)

from wagtail.admin.viewsets.chooser import ChooserViewSet

class OrganizationViewSet(SnippetViewSet):
    model = Organization
    icon = "group"
    list_display = ("name",)
    add_to_admin_menu = True
    menu_order =210
    url_prefix = "organizations"
    
    
   

class OrganizationChooserViewSet(ChooserViewSet):
    # The model can be specified as either the model class or an "app_label.model_name" string;
    # using a string avoids circular imports when accessing the StreamField block class (see below)
    model = "ropon_data.Organization"

    icon = "group"
    choose_one_text = "Choose an organization"
    choose_another_text = "Choose another organization"
    edit_item_text = "Edit this organization"
    form_fields = ["name",]  # fields to show in the "Create" tab


org_chooser_viewset = OrganizationChooserViewSet("org_chooser")

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
