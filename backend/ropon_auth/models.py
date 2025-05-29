from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.

# class RoponUser(AbstractUser):
#     # Override the email field to make it unique
#     email = models.EmailField(_("email address"),  unique=True)
    
#     # Add custom fields here as needed
#     # Currently, we are using the default fields provided by AbstractUser
    
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username', 'email']

class RoponUserManager(UserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        # Username normalization will be handled by RoponUser.normalize_username
        # and the call to super().create_user which uses it.
        # The username is passed to self.model.normalize_username by the parent class.
        user = super().create_user(username, email, password, **extra_fields)

        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        # Username normalization will be handled by RoponUser.normalize_username
        # and the call to super().create_superuser which uses it.
        # The username is passed to self.model.normalize_username by the parent class.
        return super().create_superuser(username, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        """
               Retrieves a user by username, case-insensitively.
        Also normalizes the username by stripping whitespace and converting to lowercase.
        """
        normalized_username = self.model.normalize_username(username)
        return self.get(**{self.model.USERNAME_FIELD + '__iexact': normalized_username})
    

class RoponUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True, 
                              blank=False,
                            null=False,
                            error_messages={
                                'unique': _("A user with that email already exists."),
                            })

    objects = RoponUserManager()

    @classmethod
    def normalize_username(cls, username):
        """
        Normalize the username by first applying the base class's normalization (e.g., NFKC for Unicode),
        then stripping whitespace and converting to lowercase.
        This method is used by the manager's create_user/create_superuser methods
        via the AbstractUser's create_user/create_superuser implementations.
        """
        # Apply the base class's normalization (e.g., NFKC for Unicode).
        # AbstractBaseUser.normalize_username handles if username is not a string
        # and returns a string.
        username = super().normalize_username(username)
        
        # After base normalization, apply our custom logic.
        if username:
            # The result of super().normalize_username is already a string if the input was.
            # str() conversion here is mostly for safety if the super method's contract changed
            # or if a non-string (like None) was passed initially and super handled it gracefully
            # by returning it as is.
            username = str(username).strip().lower()
        return username

    def save(self, *args, **kwargs):
        """
        Override save to ensure username is always stored in lowercase.
        This helps enforce case-insensitive uniqueness at the database level
        when combined with a unique constraint on the username field.
        """
        if self.username:
            self.username = self.username.lower() # Ensure username is lowercase before saving
        super().save(*args, **kwargs)