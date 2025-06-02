from wagtail.admin.views.pages.create import CreateView as WagtailPageCreateView
from wagtail.admin import messages

from base.messages import generate_form_validation_summary_message


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
        summary_message = generate_form_validation_summary_message(form)
        
        messages.validation_error(
            self.request,
            summary_message,
            form,  # Pass the form instance to display field-specific errors
        )
        self.has_unsaved_changes = True
        return self.render_to_response(self.get_context_data(form=form))

