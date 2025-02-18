from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.views import BaseAPIViewSet
from django.apps import apps
from django.http import Http404
from django.urls import path, reverse

from .models import ( ControlledVocabularyModel, ObservingNetworkPage,
                    Domain,
                    Discipline,
                    Region,
                    Subregion,
                    AssetType,
                    MetadataStandard,
                    AccessProtocol,
)

class ObservingNetworkPageViewSet(PagesAPIViewSet):
    model = ObservingNetworkPage

    listing_default_fields = PagesAPIViewSet.listing_default_fields + [
        'date_last_modified',
        'ropon_id'
        ]
    meta_fields =  ["locale",
                    "detail_url",
                    "slug",
                    "first_published_at",
                    "date_last_modified",
                    "alias_of"
    ]

    
# API viewsets for ControlledVocabularyClass based models

class ControlledVocabularyAPIViewSet(BaseAPIViewSet):

    listing_default_fields = BaseAPIViewSet.listing_default_fields + ["name"]

class DomainAPIViewSet(ControlledVocabularyAPIViewSet):
    model = Domain
    
class DisciplineAPIViewSet(ControlledVocabularyAPIViewSet):
    model = Discipline
    
class RegionAPIViewSet(ControlledVocabularyAPIViewSet):
    model = Region
    
class SubregionAPIViewSet(ControlledVocabularyAPIViewSet):
    model = Subregion
    
class AssetTypeAPIViewSet(ControlledVocabularyAPIViewSet):
    model = AssetType
    listing_default_fields = ControlledVocabularyAPIViewSet.listing_default_fields + ["description"]

class MetadataStandardAPIViewSet(ControlledVocabularyAPIViewSet):
    model = MetadataStandard
    listing_default_fields = ControlledVocabularyAPIViewSet.listing_default_fields + ["description","source_url"]

class AccessProtocolAPIViewSet(ControlledVocabularyAPIViewSet):
    model = AccessProtocol
    listing_default_fields = ControlledVocabularyAPIViewSet.listing_default_fields + ["description","source_url"]   
    


class ControlledVocabularyAPIViewSet(BaseAPIViewSet):
    """
    A single viewset that routes vocabulary URLs to appropriate models at runtime.
    """

    model = ControlledVocabularyModel

    # Maps URL segments (e.g. 'domains') to the actual dot-path of the model
    model_mapping = {
        "domains": "ropon_data.Domain",
        "disciplines": "ropon_data.Discipline",
        "regions": "ropon_data.Region",
        "subregions": "ropon_data.Subregion",
        "asset_types": "ropon_data.AssetType",
        "metadata_standards": "ropon_data.MetadataStandard",
        "access_protocols": "ropon_data.AccessProtocol",
    }

    def get_class_model(self, model_name):
        """
        Given a model name, return the class of the model.
        """

        if model_name is None or model_name == '':
            return self.model
        
        model_path = self.model_mapping.get(model_name)
        if not model_path:
            raise Http404(f"Invalid vocabulary type: {model_name}")
        return apps.get_model(model_path)
    


    # Add "name" to the default listing fields
    listing_default_fields = BaseAPIViewSet.listing_default_fields + ["name"]

    def dispatch(self, request, *args, **kwargs):
        model_name = kwargs.get("model_name")
        
        self.model = self.get_class_model(model_name)
        return super().dispatch(request, *args, **kwargs)
   
    @classmethod
    def get_urlpatterns(cls):
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
            path("<str:model_name>/", cls.as_view({"get": "listing_view"}), name="listing"),
            path("<str:model_name>/<int:pk>/", cls.as_view({"get": "detail_view"}), name="detail"),
        ]
    
    def listing_view(self, request, *args, **kwargs):
        """
        Wagtail calls listing_view for GETs to /<model_name>/.
        Pull 'model_name' from kwargs and set self.model accordingly.
        """
        model_name = kwargs.get("model_name",None)
        self.model = self.get_class_model(model_name)
        return super().listing_view(request)

    def detail_view(self, request, pk, *args, **kwargs):
        """
        For /cv/<model_name>/<pk>/ URLs,
        Wagtail calls detail_view for GETs to /<model_name>/<pk>/.
        Pull 'model_name' from kwargs and set self.model accordingly,
        then call the superclass detail method with pk.
        """
        model_name = kwargs.get("model_name")
        self.model = self.get_class_model(model_name)
        return super().detail_view(request, pk,)
    
    @classmethod
    def get_object_detail_urlpath(cls, model, pk, namespace=""):
        """
        Override so we can reverse with both model_name and pk.
        """
        # Look up the model_name that maps to 'model'
        # so we can pass it to reverse().
        model_name = None
        for key, path_str in cls.model_mapping.items():
            if apps.get_model(path_str) == model:
                model_name = key
                break

        if not model_name:
            return None  # No matching pattern means no detail URL

        if namespace:
            url_name = namespace + ":detail"
        else:
            url_name = "detail"

        return reverse(url_name, args=(model_name, pk))