from .views.pages.create import RoponPageCreateView
from .views.pages.edit import RoponPageEditView
from flags.urls import flagged_path
from wagtail.admin.views.pages.create import CreateView as WagtailCreateView
from wagtail.admin.views.pages.edit import EditView as WagtailEditView
app_name = 'base'

urlpatterns = [
    flagged_path( 'ROPON.BASE.USE_CUSTOM_PAGE_CREATE_EDIT_VIEWS','add/<slug:content_type_app_name>/<slug:content_type_model_name>/<int:parent_page_id>/',
         RoponPageCreateView.as_view(),
         name='add',
         fallback=WagtailCreateView.as_view(),
     ),

    flagged_path('ROPON.BASE.USE_CUSTOM_PAGE_CREATE_EDIT_VIEWS','<int:page_id>/edit/',
         RoponPageEditView.as_view(),
         name='edit',
         fallback=WagtailEditView.as_view(),
    )
]
 