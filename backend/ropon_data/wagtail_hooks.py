# ropon_data/wagtail_hooks.py

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail import hooks

from .permissions import can_publish, should_hide_submit_for_moderation
from .views.pages import ObservingNetworkPageViewSet
from .views.snippets import ControlledVocabularyGroup, org_chooser_viewset, OrganizationViewSet

from .models import ObservingNetworkPage


@hooks.register("register_admin_viewset")
def register_viewset():
    return org_chooser_viewset


register_snippet(OrganizationViewSet)


# Register the Ropon Controlled Vocabulary group 
register_snippet(ControlledVocabularyGroup)


# Register the ObservingNetworkPageViewSet
@hooks.register('register_admin_viewset')
def register_observing_network_page_viewset():
    return ObservingNetworkPageViewSet("observing_networks")



# Customize page action menu for ObservingNetworkPage based on user permissions
@hooks.register('construct_page_action_menu')
def customize_page_action_menu(menu_items, request, context):
    """
    Customizes the page action menu by:
    1. Removing publish and unpublish actions for unauthorized users
    2. Removing submit for moderation for Editors editing their own published networks
    """
    page = context.get('page')

    # Remove publish/unpublish actions for unauthorized users (existing logic)
    if not can_publish(request.user, context):
        menu_items[:] = [item for item in menu_items if item.name not in ['action-publish', 'action-unpublish']]

    # Remove submit for moderation for Editors editing their own published networks (new logic)
    if should_hide_submit_for_moderation(request.user, page):
        menu_items[:] = [item for item in menu_items if item.name.lower() != 'action-submit']


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

