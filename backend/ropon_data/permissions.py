from django.contrib.auth import get_user_model
from .models import ObservingNetworkPage, ObservingNetworkIndexPage


# check if user can publish a ObservingNetworkPage
def can_publish(user, context:dict) -> bool:
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


def should_hide_submit_for_moderation(user, page):
    """
    Returns True if 'Submit for moderation' should be hidden for this user/page combination.

    Hide submit for moderation if:
    - User is in Editors group AND
    - Page is an ObservingNetworkPage AND
    - Page is published (live=True) AND
    - User owns the page

    Args:
        user: The user attempting the action
        page: The page being edited

    Returns:
        bool: True if submit for moderation should be hidden, False otherwise
    """
    if not user.groups.filter(name='Editors').exists():
        return False

    if not isinstance(page, ObservingNetworkPage):
        return False

    # For new/unpublished pages, keep submit option available
    if not page.pk or not page.live:
        return False

    # For published pages owned by the editor, hide submit option
    return page.live and page.owner == user
