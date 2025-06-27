from django.conf import settings
from django.urls import path, include # Ensure include is imported
from django.contrib import admin
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from search import views as search_views

from wagtail.api.v2.router import WagtailAPIRouter
from ropon_data.api import (ObservingNetworkPageViewSet, 
                            ControlledVocabularyAPIViewSet
                            )
from ropon_pages.api import RoponPagesAPIViewSet
from base.api.views import RoponImagesAPIViewSet
api_router = WagtailAPIRouter("wagtailapi")

# api_router.register_endpoint("pages", PagesAPIViewSet)
api_router.register_endpoint("ropon_pages", RoponPagesAPIViewSet)
api_router.register_endpoint("networks", ObservingNetworkPageViewSet)
api_router.register_endpoint("cv", ControlledVocabularyAPIViewSet)
api_router.register_endpoint("images", RoponImagesAPIViewSet)

urlpatterns = []

# # Check the flag state from Django settings instead of querying the database
# use_custom_page_views_flag_config = settings.FLAGS.get('ROPON.BASE.USE_CUSTOM_PAGE_CREATE_EDIT_VIEWS')
# custom_views_enabled = False
# if use_custom_page_views_flag_config and isinstance(use_custom_page_views_flag_config, list) and len(use_custom_page_views_flag_config) > 0:
#     custom_views_enabled = use_custom_page_views_flag_config[0].get('value', False)

# if custom_views_enabled:
#     urlpatterns += [path('admin/pages/', include(base_urls))]  # Include custom create/edit views for pages

urlpatterns += [
    path("django-admin/", admin.site.urls),
    # Include custom Page Create and Edit views
    # only if feature flag is enabled
    path("admin/pages/",include("base.urls")),

    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),

    
    # Include the ropon_email urls under the desired path
    path("api/v2/email/", include("ropon_email.urls", namespace="ropon_email_api")),

    path('api/v2/', api_router.urls), # Keep other API router endpoints

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern.
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
