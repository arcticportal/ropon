

from wagtail.admin.views.pages.create import CreateView as WagtailPageCreateView
from wagtail.admin import messages
from django.utils.translation import gettext as _


# Custom CreateView for Wagtail Pages in the Ropon application
class RoponPageCreateView(WagtailPageCreateView):
    """
    Custom CreateView for Wagtail Pages in Ropon application to override validation error messages.
    """
    def form_invalid(self, form):
        """
        Overrides the default form_invalid behavior to show a custom message
        if required fields are missing.
        """
        has_required_error = False
        # Django's default error message for a required field is "This field is required."
        # We check against its translated version.
        required_message_text = _("This field is required.")
        for error_list in form.errors.values():
            if any(required_message_text in error for error in error_list):
                has_required_error = True
                break

        if has_required_error:
            summary_message = _("Please complete all required fields marked with an asterisk (*) before submitting the page.")
        else:
            summary_message = _("The page could not be created due to validation errors")

        messages.validation_error(
            self.request,
            summary_message,
            form,  # Pass the form instance to display field-specific errors
        )
        self.has_unsaved_changes = True
        return self.render_to_response(self.get_context_data(form=form))

