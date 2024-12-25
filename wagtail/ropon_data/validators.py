

from django.core import validators
from django.core.exceptions import ValidationError

def validate_email_or_url(value):
        email_validator = validators.EmailValidator(message="Enter a valid email address.")
        url_validator = validators.URLValidator(message="Enter a valid URL.")
        try:
            email_validator(value)
        except ValidationError:
            try:
                url_validator(value)
            except ValidationError:
                raise ValidationError("Enter a valid email address or URL.")
