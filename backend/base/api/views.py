from .serializers import RoponImageSerializer
from wagtail.images.api.v2.views import ImagesAPIViewSet

class RoponImagesAPIViewSet(ImagesAPIViewSet):
    """
    API end point to get images information with 

        1. full url for download_url
        2. width and height of the image

    """
    base_serializer_class = RoponImageSerializer
    nested_default_fields = ImagesAPIViewSet.nested_default_fields + [ "width", "height"]

