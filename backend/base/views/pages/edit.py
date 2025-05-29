
from wagtail.admin.views.pages.edit import EditView as WagtailPageEditView
from wagtail.admin import messages
from django.utils.translation import gettext as _


# Custom EditView for Wagtail pages in the Ropon application
class RoponPageEditView(WagtailPageEditView):
    """
    Custom EditView for Wagtail Pages in Ropon application to override validation error messages.
    """
    def form_invalid(self, form):
        """
        Overrides the default form_invalid behavior to show a custom message
        if required fields are missing, while preserving other functionalities
        like workflow cancellation and lock handling.
        """
        # Handle workflow cancellation and page locks, replicating logic from WagtailEditView.form_invalid
        # Safely check attributes that might not be present in all scenarios (e.g. no workflow).
        if getattr(self, 'is_cancelling_workflow', False):
            if (hasattr(self, 'workflow_state') and self.workflow_state and
                    hasattr(self.workflow_state, 'cancel') and
                    hasattr(self, 'add_cancel_workflow_confirmation_message') and
                    hasattr(self, 'page') and hasattr(self.page, 'get_lock')):
                
                self.workflow_state.cancel(user=self.request.user)
                self.add_cancel_workflow_confirmation_message()

                self.lock = self.page.get_lock()
                self.locked_for_user = self.lock is not None and self.lock.for_user(
                    self.request.user
                )
            # If the above conditions for workflow cancellation aren't fully met,
            # it will fall through, and standard lock/validation messages will apply.

        elif getattr(self, 'locked_for_user', False):
            messages.error(
                self.request, _("The page could not be saved as it is locked")
            )
        else:
            # Custom validation message logic
            has_required_error = False
            required_message_text = _("This field is required.")
            for error_list in form.errors.values():
                if any(required_message_text in error for error in error_list):
                    has_required_error = True
                    break

            if has_required_error:
                summary_message = _("Please complete all required fields marked with an asterisk (*) before submitting the page.")
            else:
                summary_message = _("The page could not be saved due to validation errors")

            messages.validation_error(
                self.request,
                summary_message,
                form,  # Pass the form instance
            )

        # Common tail part from WagtailEditView.form_invalid
        self.errors_debug = repr(form.errors)
        if hasattr(form, 'formsets'):
             self.errors_debug += repr(
                [
                    (name, formset.errors)
                    for (name, formset) in form.formsets.items()
                    if formset.errors
                ]
            )
        self.has_unsaved_changes = True

        if hasattr(self, 'get_page_for_status'):
            self.page_for_status = self.get_page_for_status()
        elif hasattr(self, 'page'): # Fallback
             self.page_for_status = self.page


        return self.render_to_response(self.get_context_data(form=form))

