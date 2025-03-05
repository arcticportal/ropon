

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _  # Import translation function
import datetime
import requests

def validate_email_or_url(value):
        """Validate that a given value is either a valid email address or URL, raising ValidationError if neither."""
        email_validator = validators.EmailValidator(message="Enter a valid email address.")
        url_validator = validators.URLValidator(message="Enter a valid URL.")
        try:
            email_validator(value)
        except ValidationError:
            try:
                url_validator(value)
            except ValidationError:
                raise ValidationError("Enter a valid email address or URL.")

def validate_start_year(value):
    """Validates that the input year is not in the future by comparing it with the current year."""
    current_year = datetime.datetime.now().year
    if value > current_year:
        raise ValidationError('Year started cannot be in the future.')



def validate_latitude(value):
    if not -90 <= value <= 90:
        raise ValidationError('Latitude must be between -90 and 90 degrees')

def validate_longitude(value):
    if not -180 <= value <= 180:
        raise ValidationError('Longitude must be between -180 and 180 degrees')

def validate_soso_bounding_box(value):
    sw = value['southwest']
    ne = value['northeast']
    if sw['latitude'] >= ne['latitude']:
        raise ValidationError('Northern latitude must be greater than southern latitude')
    if sw['longitude'] == ne['longitude']:
        raise ValidationError('Bounding Box cannot be a line. Eastern longitude cannot be same as western longitude')
    
def validate_bounding_box(value):
    if value['north'] <= value['south']:
        raise ValidationError('Northern latitude must be greater than southern latitude')
    if value['east'] == value['west']:
        raise ValidationError('Bounding Box cannot be a line. Eastern longitude cannot be same as western longitude')
    

def validate_image_url(value, valid_extensions=None):
    """
    Validate a URL to ensure it points to a valid image file.
    
    Args:
        value: The URL to validate
        valid_extensions: Optional list of valid file extensions (e.g. ['.png', '.jpg']). 
                        Defaults to ['.png', '.jpg', '.jpeg', '.svg']
    
    Raises:
        ValidationError: If the URL is invalid, inaccessible, or doesn't point to an image
    """
    if not valid_extensions:
        valid_extensions = ['.png', '.jpg', '.jpeg', '.svg']
    
    if not any(value.lower().endswith(ext) for ext in valid_extensions):
        raise ValidationError(_('Invalid logo URL. Must be one of: {}').format(', '.join(valid_extensions)))
    
    try:
        response = requests.head(value, allow_redirects=True)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            raise ValidationError(_('URL does not point to an image file.'))
    except requests.RequestException as e:
        raise ValidationError(_('Cannot access the image URL: {}').format(str(e)))

