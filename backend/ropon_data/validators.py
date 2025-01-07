

from django.core import validators
from django.core.exceptions import ValidationError
import datetime

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

