from django_filters.fields import ModelChoiceField

class UserModelChoiceField(ModelChoiceField):
    """
    Custom ModelChoiceField that displays users by their full name.
    If full name is not available, falls back to username.
    

    """
    def label_from_instance(self, user) -> str:
        """
        Customize the display label for each user in the dropdown.
        
        Args:
            user: User instance to get label for
            
        Returns:
            str: User's full name or username if full name is empty
        """
        full_name = user.get_full_name().strip()
        return full_name if full_name else user.username
