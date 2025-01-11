


# Using Wagtail signals for page publishing events

def update_owner_authorization_on_publish(sender, instance, **kwargs):
    """
    Updates 'is_owner_authorized' field to True when an ObservingNetworkPage is published,
    using Wagtail's page_published signal.
    """

    instance.is_owner_authorized = True
    instance.save()
