"""
Custom serializers for the RoPON API.

This module contains serializers that customize the default Wagtail API behavior
for ObservingNetworkPage endpoints.
"""
from rest_framework.fields import SkipField
from wagtail.api.v2.serializers import PageSerializer, Field
from wagtail.api.v2.utils import get_full_url


class RoponIdDetailUrlField(Field):
    """
    Custom DetailUrlField that uses ropon_id instead of pk in the URL.

    This field generates detail URLs like /api/v2/networks/<ropon_id>/
    instead of the default /api/v2/networks/<pk>/.

    No extra DB query is needed because ropon_id is already loaded on the
    instance (it's included in listing_default_fields).
    """
    def get_attribute(self, instance):
        # Use ropon_id instead of pk - already loaded on instance
        ropon_id = getattr(instance, 'ropon_id', None)
        if ropon_id:
            url_path = self.context["router"].get_object_detail_urlpath(
                type(instance), ropon_id
            )
            if url_path:
                return get_full_url(self.context["request"], url_path)
        raise SkipField

    def to_representation(self, url):
        return url


class ObservingNetworkPageSerializer(PageSerializer):
    """
    Custom serializer for ObservingNetworkPage that uses ropon_id in detail_url.

    Overrides the default detail_url field from BaseSerializer to use
    ropon_id instead of the page's primary key in the URL.
    """
    detail_url = RoponIdDetailUrlField(read_only=True)
