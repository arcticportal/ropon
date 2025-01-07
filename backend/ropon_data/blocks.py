from wagtail.blocks import StructBlock, FloatBlock
from django.core.exceptions import ValidationError
from .validators import validate_latitude, validate_longitude

class BoundingBoxBlock(StructBlock):
    north = FloatBlock(validators=[validate_latitude], help_text="Northern latitude (-90 to 90)")
    south = FloatBlock(validators=[validate_latitude],  help_text="Southern latitude (-90 to 90)")
    east = FloatBlock(validators=[validate_longitude], help_text="Eastern longitude (-180 to 180)")
    west = FloatBlock(validators=[validate_longitude],  help_text="Western longitude (-180 to 180)")

    class Meta:
        icon = 'site'
        label = 'Bounding Box Coordinates'
        form_classname = 'bounding-box-block struct-block'
        
    def clean(self, value):
        cleaned_data = super().clean(value)
        if cleaned_data['north'] <= cleaned_data['south']:
            raise ValidationError('Northern latitude must be greater than southern latitude')
        return cleaned_data