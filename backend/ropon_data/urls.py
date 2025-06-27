from django.urls import path

from ropon_data.views.pages import (
    ObservingNetworkCreateView,
    ObservingNetworkEditView,
)

app_name = 'ropon_data'

urlpatterns = [
    path('create/<int:parent_page_id>/observing_network/',
         ObservingNetworkCreateView.as_view(),
         name='add-observing-network'),
    
    path('<int:page_id>/edit/',
         ObservingNetworkEditView.as_view(),
         name='edit-observing-network'),
]
