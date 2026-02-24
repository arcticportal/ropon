from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.views import BaseAPIViewSet
from django.apps import apps
from django.http import Http404, JsonResponse
from django.urls import path, reverse
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from flags.state import flag_enabled
import sys
from ropon_data.models import (ControlledVocabularyModel, ObservingNetworkPage)
from ropon_data.serializers import ObservingNetworkPageSerializer
from ropon_data.renderers import ObservingNetworkCSVRenderer
from flags.urls import flagged_path

ROPON_ID_FLAG = 'ROPON.DATA.ENABLE_ON_API_ROPONID_DETAILS'


class ObservingNetworkPageViewSet(PagesAPIViewSet):
    """
    API endpoint to get Observing Networks information.

    List all Observing Networks are available on the root URL.
    Supports CSV export via ?format=csv query parameter (list view only).

    Retrieve a specific Observing Network by either:
    - Page ID at /api/v2/networks/<id>/
    - RoPON ID at /api/v2/networks/<ropon_id>/

    Both methods will return identical responses.
    Note: Detail view only supports JSON format.
    """
    model = ObservingNetworkPage
    base_serializer_class = ObservingNetworkPageSerializer

    # Add CSV renderer for format=csv support (issue #224)
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, ObservingNetworkCSVRenderer]

    # Inherit from parent and modify (issue #225):
    # - Remove 'title', add 'name' as replacement
    # - Add 'date_last_modified' and 'ropon_id'
    listing_default_fields = [
        f for f in PagesAPIViewSet.listing_default_fields if f != 'title'
    ] + [ 'ropon_id', 'name', 'date_last_modified' ]

    # Inherit from parent and remove 'slug' (issue #225)
    # Note: The exclusion list is inlined below because accessing a class-scope variable
    # inside a list comprehension causes a NameError in Python 3.
    meta_fields = [
        f for f in PagesAPIViewSet.meta_fields
        if f not in ['type','slug','html_url', 'show_in_menus','seo_title', 'search_description','alias_of','parent']
    ] + ['date_last_modified', 'last_modified_by']

    # remove title field from body fields, add name field for #225
    body_fields = [f for f in PagesAPIViewSet.body_fields
                   if f !='title'] + ['name']

    @classmethod
    def get_urlpatterns(cls):
        '''
        Override the default URL patterns to include the ropon_id pattern.
        '''

        # if not flag_enabled(ROPON_ID_FLAG):
        #     return super().get_urlpatterns()

        ropon_id_pattern = "<uuid:ropon_id>/"
        # ropon_id_path = path(ropon_id_pattern, cls.as_view({"get": "detail_view"}), name="detail")
        ropon_id_path = flagged_path( ROPON_ID_FLAG , ropon_id_pattern, cls.as_view({"get": "detail_view"}), name="detail", )

        return [ropon_id_path,] + super().get_urlpatterns()

    def listing_view(self, request):
        """
        List all Observing Networks.

        For CSV format (?format=csv), returns all records without pagination.
        For JSON format, uses standard Wagtail pagination.
        """
        # Check if CSV format is requested
        if hasattr(request, 'accepted_renderer') and request.accepted_renderer.format == 'csv':
            # For CSV export, request all fields from the serializer.
            # The renderer's CSV_COLUMNS controls which fields appear in output,
            # filtering out unwanted fields like logo_image.
            request.GET = request.GET.copy()
            request.GET['fields'] = '*'
            FILE_NAME = "observing_networks_list.csv"
            # Return all records without pagination for CSV
            queryset = self.get_queryset()
            self.check_query_parameters(queryset)
            queryset = self.filter_queryset(queryset)
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)
            response['Content-Disposition'] = f'attachment; filename="{FILE_NAME}"'
            return response

        # Default behavior for JSON with pagination
        return super().listing_view(request)

    def detail_view(self, request, *args, **kwargs):
        """
        Retrieve a specific Observing Network by either:
        - Page ID at /api/v2/networks/<id>/
        - RoPON ID at /api/v2/networks/<ropon_id>/

        Both methods will return identical responses.
        Note: CSV format is not supported for detail view.
        """
        # Reject CSV format for detail view (issue #224)
        # Use JsonResponse to force JSON content type regardless of content negotiation
        if request.query_params.get('format') == 'csv':
            return JsonResponse(
                {'error': 'CSV format is not supported for single record views. Use the list endpoint instead. For single record retrieval, use JSON format with /api/v2/networks/<ropon_id>/'},
                status=400
            )

        uuid_value = kwargs.get('ropon_id', False)
        if uuid_value and flag_enabled(ROPON_ID_FLAG):
            sys.stderr.write(f"Using RoPON ID: {uuid_value}\n")
            self.lookup_field = 'ropon_id'
            pk_value = uuid_value
        else:
            pk_value = kwargs.get(self.lookup_field, False)

        response = super().detail_view(request, pk_value)

        return response


class ControlledVocabularyAPIViewSet(BaseAPIViewSet):
    """
    Common API to serve up RoPON controlled vocabulary models

    url patterns are using pluralized names, e.g. /cv/domains/ or /cv/disciplines/
    these are used to derive the model class to use for the viewset.

    Details for each specific controlled vocabulary type are available at /cv/<cv_name>/<id>/
    e.g. /cv/domains/1/ or /cv/disciplines/2/

    """

    model = ControlledVocabularyModel

    @classmethod
    def get_subclass_model_strings(cls):
        """
        Return a list of model names that are subclasses of ControlledVocabularyModel.
        """
        return [model.__name__ for model in ControlledVocabularyModel.__subclasses__()]

    def get_class_model(self, model_name):
        """
        Given a model name, return the class of the model.
        """

        submodels = self.get_subclass_model_strings()
        cv_urls = ", ".join([f"{model.lower()}s" for model in submodels])

        if model_name is None or model_name == '':
            return self.model

        app_label = self.model._meta.app_label
        model_path = f"{app_label}.{model_name[:-1]}"

        try:
            return apps.get_model(model_path)
        except LookupError:
            raise Http404(f"Invalid url pattern: {model_name}. Use a specific controlled vocabulary type. \nValid types are: {cv_urls}")


    # Add "name" to the default listing fields
    listing_default_fields = BaseAPIViewSet.listing_default_fields + ["name", "sort_order"]

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

        if not model_name:
            combined_data = {}
            for submodel_name in self.get_subclass_model_strings():
                plural_name = submodel_name.lower() + "s"
                submodel = self.get_class_model(plural_name)
                queryset = submodel.objects.all().order_by("id")
                self.model = submodel
                serializer = self.get_serializer(queryset, many=True)
                combined_data[plural_name] = serializer.data
            return Response(combined_data)

        else:
            self.model = self.get_class_model(model_name)
            return super().listing_view(request)

    def detail_view(self, request, pk, *args, **kwargs):
        """
        For /cv/<model_name>/<pk>/ URLs,
        Wagtail calls detail_view for GETs to /<model_name>/<pk>/.
        Pull 'model_name' from kwargs and set self.model accordingly,
        then call the superclass detail method with pk.
        """
        model_name = kwargs.get("model_name", None)
        self.model = self.get_class_model(model_name)
        return super().detail_view(request, pk,)

    @classmethod
    def get_object_detail_urlpath(cls, model, pk, namespace=""):
        """
        Override so we can reverse with both model_name and pk.
        """
        # Look up the model_name that maps to 'model'
        # so we can pass it to reverse().
        # Get the model name from the model's meta attributes and pluralize it
        model_name = model._meta.model_name + 's'

        if not model_name:
            return None  # No matching pattern means no detail URL

        if namespace:
            url_name = namespace + ":detail"
        else:
            url_name = "detail"

        return reverse(url_name, args=(model_name, pk))
