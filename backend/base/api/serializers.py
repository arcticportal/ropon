
from wagtail.images.api.v2.serializers import ImageSerializer, ImageDownloadUrlField
from django.conf import settings


class RoponImageDownloadUrlField(ImageDownloadUrlField):
    """
    Serializes the "download_url" field as absolute url for images.

    Example:
    "download_url": "https://hostname:port/media/images/a_test_image.jpg"
    """

    def to_representation(self, image):
        return self.full_url(image.file.url)
    

    def full_url(self, url):
        if hasattr(settings, "WAGTAILADMIN_BASE_URL") and url.startswith("/"):
            url = settings.WAGTAILADMIN_BASE_URL + url
        return url

       
class RoponImageSerializer(ImageSerializer):
    download_url = RoponImageDownloadUrlField(read_only=True)
