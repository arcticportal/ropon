
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext as _ # Use lazy for top-level definitions

def generate_form_validation_summary_message(form):
    """
    Generates a formatted HTML summary message for form validation errors.

    Args:
        form: The Django form instance containing errors.

    Returns:
        An HTML string representing the summary message.
    """
    has_required_error = False
    # Django's default error message for a required field is "This field is required."
    # We check against its translated version.
    required_message_text = _("This field is required.")
    for error_list in form.errors.values():
        if any(required_message_text in error for error in error_list):
            has_required_error = True
            break  # Exit early if a required field error is found

    # Start with a general error message.
    # This message will be displayed if there are any validation errors.
    # Construct the summary message using HTML for better formatting.
    top_line = _("The page could not be saved due to validation errors or missing information. Correct the errors below before submitting the page.")
    bullet_point_1 = _("Please review the form and check the errors highlighted below for each field.")

    # Prepare content for list items. Each item in the list is a tuple of arguments for the format string.
    list_item_args = [
        (bullet_point_1,),
    ]

    if has_required_error:
        bullet_point_2 = _("Ensure all fields marked with an asterisk (*) are completed.")
        list_item_args.append((bullet_point_2,))

    # Generate HTML for the list items using format_html_join.
    # The first argument is the separator (none needed here as <li></li> provides structure).
    # The second argument is the format string for each list item.
    # The third argument is an iterable of tuples, where each tuple contains arguments for one list item.
    list_items_html = format_html_join(
        '',  # No separator between list items
        "<li>{}</li>",  # Format string for each item
        list_item_args
    )

    # Construct the final summary message using format_html.
    summary_message = format_html(
        "{}<ul class='top-validation-error-list'>{}</ul>",
        top_line,
        list_items_html
    )
    return summary_message
