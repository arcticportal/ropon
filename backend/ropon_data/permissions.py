
from django.contrib.auth.models import User
from wagtail.models import Page
from .models import ObservingNetworkPage, ObservingNetworkIndexPage


# check if user can publish a ObservingNetworkPage
def can_publish(user: User, context:dict) -> bool:
    view = context.get('view')
    page = context.get('page',None)
    parent_page = context.get('parent_page',None)

    if user.is_superuser or user.groups.filter(name='Moderators').exists():
        return True
    
    if user.groups.filter(name='Editors').exists() :
        
        if view == 'create' and isinstance(parent_page, ObservingNetworkIndexPage):
            return False
        if view == 'edit' and isinstance(page, ObservingNetworkPage):
            return page.is_owner_authorized and page.owner == user
            
    return True

