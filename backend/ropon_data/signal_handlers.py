
from wagtail.signals import page_published
from django.dispatch import receiver
from ropon_data.models import ObservingNetworkPage
from wagtail.admin.signal_handlers import workflow_submission_email_notifier
from wagtail.models import WorkflowState
from wagtail.signals import workflow_submitted
# Using Wagtail signals for page publishing events

@receiver(page_published, sender=ObservingNetworkPage)
def update_owner_authorization_on_publish_signal_handler(sender, instance, **kwargs):
    """
    Updates 'is_owner_authorized' field to True when an ObservingNetworkPage is published,
    using Wagtail's page_published signal.
    """

    instance.is_owner_authorized = True
    instance.save()

def register_signal_handlers():
    """
    Registers the signal handlers for the application.
    This includes connecting the page_published signal to the update_owner_authorization_on_publish function.
    """

    page_published.connect(update_owner_authorization_on_publish_signal_handler, sender=ObservingNetworkPage)

    # Disconnect task submission email notifier to prevent sending emails
    # task_submitted.disconnect(
    #     task_submission_email_notifier,
    #     sender=TaskState,
    #     dispatch_uid="group_approval_task_submitted_email_notification",
    # )
    # Disconnect workflow submission email notifier to prevent sending emails
    workflow_submitted.disconnect(
        workflow_submission_email_notifier,
        sender=WorkflowState,
        dispatch_uid="workflow_state_submitted_email_notification",
    )
