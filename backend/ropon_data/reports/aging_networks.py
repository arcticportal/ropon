from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import django_filters
from django.core.exceptions import PermissionDenied
from flags.state import flag_enabled
from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.widgets import AdminDateInput
from wagtail.admin.views.reports.aging_pages import AgingPagesView
from ropon_data.models import ObservingNetworkPage, Organization, ObservingNetworkOrganization

User = get_user_model()

class AgingNetworksReportFilterSet(WagtailFilterSet):
    """
    FilterSet for AgingObservingNetworks report that provides filters for:
    - Last published date
    - Owner of the network
    - Organization
    """
    last_published_at = django_filters.DateTimeFilter(
        label=_("Last published before"), 
        lookup_expr="lte", 
        widget=AdminDateInput
    )
    owner = django_filters.ModelChoiceFilter(
        label=_("Owner"),
        queryset=User.objects.all(),
        empty_label=_("Any owner")
    )
    organization = django_filters.ModelChoiceFilter(
        label=_("Organization"),
        queryset=Organization.objects.all(),
        empty_label=_("Any organization"),
        method='filter_by_organization'
    )

    def filter_by_organization(self, queryset, name, value):
        """
        Filter the queryset to only include networks that are associated with the selected organization.
        Args:
            queryset: Base queryset of ObservingNetworkPage instances
            name: Name of the filter field
            value: Selected Organization instance
        Returns:
            Filtered queryset containing only networks associated with the selected organization
        """
        if value:
            # Get all network_organizations that have the selected organization
            return queryset.filter(
                id__in=ObservingNetworkOrganization.objects.filter(
                    organization=value
                ).values_list('observingnetwork_id', flat=True)
            )
        return queryset

    class Meta:
        model = ObservingNetworkPage
        fields = ["live", "last_published_at", "owner", "organization"]


class AgingObservingNetworksView(AgingPagesView):
    """
    A custom report view that shows aging observing networks.
    This report is available to:
    - Users in the Moderators group when the feature flag is enabled
    - Superusers (regardless of group membership)
    """
    results_template_name = "wagtailadmin/reports/aging_networks_results.html"
    page_title = _("Aging Observing Networks")
    header_icon = "time"
    filterset_class = AgingNetworksReportFilterSet
    index_url_name = "aging_networks"
    index_results_url_name = "aging_networks_results"
    # template_name = "wagtailadmin/reports/aging_networks.html"
    

    export_headings = {
        "status_string": _("Status"),
        "last_published_at": _("Last published at"),
        "last_published_by_user": _("Last published by"),
        "owner": _("Owner"),
    }
    list_export = [
        "title",
        "status_string",
        "last_published_at",
        "last_published_by_user",
        "owner",
    ]

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user has permission to view the report.
        Access is granted to:
        - Superusers
        - Users in Moderators group when feature flag is enabled
        """
        if not request.user.is_superuser:
            if not flag_enabled('ROPON.REPORTS.AGING_OBSERVING_NETWORKS'):
                raise PermissionDenied
            
            if not request.user.groups.filter(name='Moderators').exists():
                raise PermissionDenied
                
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """
        Get queryset filtered to only ObservingNetworkPage instances
        that the user has publish permission for
        """
        queryset = super().get_queryset()
        return queryset.filter(content_type__model='observingnetworkpage')

