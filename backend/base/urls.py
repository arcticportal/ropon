from django.urls import path
from .views.pages.create import RoponPageCreateView
from .views.pages.edit import RoponPageEditView

app_name = 'base'

urlpatterns = [
    path( 'add/<slug:content_type_app_name>/<slug:content_type_model_name>/<int:parent_page_id>/',
         RoponPageCreateView.as_view(),
         name='add'),

    path('<int:page_id>/edit/',
         RoponPageEditView.as_view(),
         name='edit'),
]
    