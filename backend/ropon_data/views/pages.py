# Define custom PageViewSet, PageIndex and PageViews classes for Ropon data


from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.admin.views.pages.listing import IndexView
from ropon_data.models import ObservingNetworkPage
from wagtail.admin.ui.tables import Column


class ObservingNetworkPageIndexView(IndexView):
    def get_base_queryset(self):
        queryset = super().get_base_queryset()
        if self.request.user.groups.filter(name='Editors').exists():
            queryset = queryset.filter(owner=self.request.user)
        return queryset

class ObservingNetworkFilterSet(PageListingViewSet.filterset_class):
    class Meta:
        model = ObservingNetworkPage
        fields = [
                  
                  ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove unwanted fields
        self.filters.pop("site", None)
        self.filters.pop("has_child_pages", None)


class ObservingNetworkPageViewSet(PageListingViewSet):
    model = ObservingNetworkPage
    menu_label = 'Observing Networks'
    menu_name = 'observing_network_pages'
    menu_icon = 'doc-full'
    # list_display = ('name', 'organization_name', 'owner', 'last_modified_by')
    # columns =  [
    #     BulkActionsColumn("bulk_actions"),
    #     PageTitleColumn('name', label='Name', classname='name'),
    #     Column('abbreviation', label='Abbreviation', classname='abbreviation'),
    #     PageStatusColumn('status', label='Status', classname='status', sort_key='live'),
    #     DateColumn('date_last_modified', label='Last Updated', classname='date_last_modified'),
    #     ]

    columns = PageListingViewSet.columns +[
        Column('abbreviation', label='Abbreviation', classname='abbreviation'),
    ]
    
    filterset_class = ObservingNetworkFilterSet
    index_view_class = ObservingNetworkPageIndexView
    search_fields = ('name', 'description', 'abbreviation')
    menu_order = 150  # Adjust the order as needed
    add_to_admin_menu = True

    