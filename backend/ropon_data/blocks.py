from cProfile import label
from tokenize import group
from wsgiref.validate import validator
from wagtail.blocks import StructBlock, FloatBlock
from django.core.exceptions import ValidationError
from .validators import (
    validate_soso_bounding_box,
    validate_latitude,
    validate_longitude,
    validate_bounding_box
)


class BoundingBoxBlock(StructBlock):
    south = FloatBlock(validators=[validate_latitude], label='Southern Latitude')
    west = FloatBlock(validators=[validate_longitude],  label='Western Longitude')
    north = FloatBlock(validators=[validate_latitude], label='Northern Latitude')
    east = FloatBlock(validators=[validate_longitude], label='Eastern Longitude')
    
    class Meta:
        icon = 'site'
        label = 'Bounding Box Coordinates'
        form_classname = 'bounding-box-block struct-block'
        
    def clean(self, value):
        cleaned_data = super().clean(value)
        validate_bounding_box(cleaned_data)
        return cleaned_data


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
        label = 'SOSO Bounding Box'
        form_classname = 'soso-bounding-box-block struct-block'
        label_format = 'SOSO box - {southwest} ; {northeast}'

    def clean(self, value):
        cleaned_data = super().clean(value)
        validate_soso_bounding_box( cleaned_data)
        return cleaned_data