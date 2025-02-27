
from django_filters import ModelChoiceFilter
from .fields import UserModelChoiceField


class UserModelChoiceFilter(ModelChoiceFilter):
    """
    Custom ModelChoiceFilter that displays users by their full name.
    If full name is not available, falls back to username.
    """
    
    field_class = UserModelChoiceField
