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
    

def validate_image_url(value, valid_extensions=None, timeout=5):
    """
    Validate a URL to ensure it points to a valid image file.
    
    Args:
        value: The URL to validate
        valid_extensions: Optional list of valid file extensions
                         Defaults to ['.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp']
        timeout: Request timeout in seconds (default: 5)
    
    Raises:
        ValidationError: If the URL is invalid, inaccessible, or doesn't point to an image
    """
    # Default allowed extensions (expanded list)
    if not valid_extensions:
        valid_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp']
    
    # Skip extension validation if URL doesn't have a clear extension (some CDNs don't use extensions)
    url_lower = value.lower()
    has_extension = any(url_lower.endswith(ext) for ext in valid_extensions)
    
    # Only validate extension if the URL appears to have a file extension
    if '.' in url_lower.split('/')[-1] and not has_extension:
        raise ValidationError(
            f'Invalid image format. Must be one of: {", ".join(valid_extensions)}',
            code='invalid_image_extension',
        )
    
    # Validate URL accessibility and content type
    try:
        # First try a HEAD request for efficiency
        response = requests.head(value, allow_redirects=True, timeout=timeout)
        
        # If HEAD request fails or doesn't provide content-type, try GET with range
        if response.status_code >= 400 or not response.headers.get('content-type', '').startswith('image/'):
            # Try a partial GET request to verify it's an image
            headers = {'Range': 'bytes=0-1023'}  # Get first 1KB to check if it's an image
            response = requests.get(value, timeout=timeout, headers=headers, stream=True)
            response.raise_for_status()
            
            # Check if content-type indicates an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                raise ValidationError(
                    f'URL does not appear to point to an image file. Content type: {content_type}',
                    code='invalid_image_content',
                )
    
    except requests.exceptions.Timeout:
        raise ValidationError(
            f'Logo download timed out from {value}. Please check the URL or try again later.',
            code='timeout_error',
        )
    except requests.exceptions.ConnectionError:
        raise ValidationError(
            f'Unable to connect to {value}. Please verify the URL is correct and accessible.',
            code='connection_error',
        )
    except requests.exceptions.HTTPError as e:
        # Check if we have a response with status code info
        if hasattr(e, 'response') and e.response is not None:
            status_info = f"{e.response.status_code} {e.response.reason}"
        else:
            status_info = str(e)
        
        raise ValidationError(
            f'HTTP error accessing image: {value} : {status_info}',
            code='http_error',
        )
    except requests.exceptions.RequestException as e:
        raise ValidationError(
            f'Failed to access image: {str(e)}',
            code='request_error',
        )
    except Exception as e:
        raise ValidationError(
            f'Unexpected error while validating image: {str(e)}',
            code='unexpected_error',
        )

