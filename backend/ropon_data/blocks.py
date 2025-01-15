from cProfile import label
from tokenize import group
from wsgiref.validate import validator
from wagtail.blocks import StructBlock, FloatBlock
from django.core.exceptions import ValidationError
from .validators import (
    validate_soso_bounding_box,
    validate_latitude,
    validate_longitude,

)


class GeoPointBlock(StructBlock):
    latitude = FloatBlock(validators=[validate_latitude], label='Latitude')
    longitude = FloatBlock(validators=[validate_longitude], label='Longitude')
    
    class Meta:
        icon = 'site'
        label = 'Geographic Point Coordinates'
        form_classname = 'geopoint-block struct-block'
        label_format = '{latitude} , {longitude}'

class SOSOBoundingBoxBlock(StructBlock):
    southwest = GeoPointBlock(label='SouthWest Corner')
    northeast = GeoPointBlock(label='NorthEast Corner')
    
    class Meta:
        icon = 'site'
        label = 'Bounding Box'
        form_classname = 'soso-bounding-box-block struct-block'
        label_format = 'BBox - {southwest} ; {northeast}'

    def clean(self, value):
        cleaned_data = super().clean(value)
        validate_soso_bounding_box( cleaned_data)
        return cleaned_data