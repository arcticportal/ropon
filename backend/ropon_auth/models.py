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
        
        user = super().create_user(username,email, password,**extra_fields)

        return user
    
    def create_superuser(self, username,email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        return super().create_superuser(username, email, password, **extra_fields)


class RoponUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True, 
                              blank=False,
                            null=False,
                            error_messages={
                                'unique': _("A user with that email already exists."),
                            })

    objects = RoponUserManager()