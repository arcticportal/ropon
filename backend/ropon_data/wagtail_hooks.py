# ropon_data/wagtail_hooks.py

from django.shortcuts import redirect
from django.urls import reverse
from wagtail.snippets.models import register_snippet
from wagtail import hooks

from .permissions import can_publish
from .views.pages import ObservingNetworkPageViewSet
from .views.snippets import ControlledVocabularyGroup

from .models import ObservingNetworkPage


# Register the Ropon Controlled Vocabulary group 
register_snippet(ControlledVocabularyGroup)


# Register the ObservingNetworkPageViewSet
@hooks.register('register_admin_viewset')
def register_observing_network_page_viewset():
    return ObservingNetworkPageViewSet("observing_networks")


# On approval and publish of ObservingNetworkPage, update is_owner_authorized field
@hooks.register('after_publish_page')
def update_is_owner_authorized_on_publish(request, page):
    """
    Updates 'is_owner_authorized' field to True when an ObservingNetworkPage is published.
    """
    if isinstance(page, ObservingNetworkPage):
        page.is_owner_authorized = True
        page.save()

# If ObservingNetworkPage is edited by Editors group and is_owner_authorized is True, and request.user is not owner then remove publish from the page_action_menu
@hooks.register('construct_page_action_menu')
def remove_publish_from_page_action_menu(menu_items, request, context):
    """
    Removes publish and unpublish actions from the page action menu for unauthorized users.
    """
    if not can_publish(request.user, context):
        menu_items[:] = [item for item in menu_items if item.name not in ['action-publish', 'action-unpublish']]


@hooks.register('construct_explorer_page_queryset')
def show_authors_only_their_pages(parent_page, pages, request):
    """
    Modifies the queryset of pages displayed in the Wagtail admin explorer.
    Editors only see pages they own.
    """
    if request.user.groups.filter(name='Editors').exists():
        pages = pages.filter(owner=request.user)
    return pages

@hooks.register('after_create_page')
def redirect_after_create_page(request, page):
    """
    Redirects to the listing view URL after creating an ObservingNetworkPage.
    """
    if isinstance(page, ObservingNetworkPage):
        return redirect(reverse("observing_networks:index"))

@hooks.register('after_edit_page')
def redirect_after_edit_page(request, page):
    """
    Redirects to the listing view URL after editing an ObservingNetworkPage.
    """
    if isinstance(page, ObservingNetworkPage):
        return redirect(reverse("observing_networks:index"))
    

@hooks.register('insert_global_admin_css')
def global_admin_css():
    return '<link rel="stylesheet" href="/static/ropon_data/css/ropon_data.css">'