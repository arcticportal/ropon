"""
Serializers for the ropon_email app.
"""
import logging
import time

from rest_framework import serializers

logger = logging.getLogger(__name__)

# Honeypot candidate field names. The frontend renders ONE of these at random
# per form mount (see angular/src/app/contact/contact.component.ts honeypotCandidates).
# MUST stay in sync between the two lists. We never expose this set over the API,
# otherwise a bot could learn the full candidate set at once. The names are
# deliberately OUTSIDE browser autofill vocabulary so auto form fill never
# populates the trap for genuine users.
HONEYPOT_FIELDS = ['fax_number', 'web_address2', 'contact_ref', 'alt_phone2', 'org_ref', 'site_link2']

# Minimum time (seconds) a human is expected to spend on the form. Submissions
# faster than this are treated as a bot. Soft signal: fail-open on
# missing/garbage/negative timestamps so real users aren't blocked.
MIN_FORM_SECONDS = 3


class ContactFormSerializer(serializers.Serializer):
    """
    Serializer for validating the contact form data.

    Detection of likely-bot submissions happens in ``validate()`` by inspecting
    the raw request payload via ``self.context['request'].data``. DRF drops
    unknown fields before ``validate()`` runs, so the honeypot/``_ts`` fields
    must be read from the raw payload, not from ``attrs``. When a bot is
    detected the flag ``bot_detected`` is set instead of raising: the view then
    returns a silent HTTP 200 so the bot can't tell it was caught.

    A submission is flagged as a bot when it arrives faster than a human could
    manage (``_ts`` younger than ``MIN_FORM_SECONDS``) -- with or without a
    tripped honeypot. A filled honeypot on a human-timescale submit (e.g. a
    genuine user whose browser auto-filled the form) is logged as a warning
    but the message is still delivered -- losing a real email is considered
    worse than letting some spam through.
    """
    name = serializers.CharField(max_length=100, required=True)
    from_email_id = serializers.EmailField(required=True)
    message = serializers.CharField(required=True)

    # Flag consulted by the view after is_valid(); set in validate().
    bot_detected: bool = False

    def validate_name(self, value):
        """
        Basic validation for the name field.
        """
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        # Add more specific validation if needed (e.g., prevent numbers)
        return value

    def validate_message(self, value):
        """
        Basic validation for the message field.
        """
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        # Add more specific validation if needed (e.g., length limits)
        return value

    def validate(self, attrs):
        """
        Detect likely-bot submissions from the raw payload.

        Reads ``self.context['request'].data`` (the unparsed payload) because
        DRF strips any field not declared on the serializer before this method
        runs. On detection sets ``self.bot_detected = True`` and returns
        cleanly (does NOT raise) so the view can emit a silent 200.

        Combined rule: ``bot_detected`` is set whenever ``_ts`` shows an
        implausibly fast submit (a human cannot complete the form that
        quickly); a tripped honeypot strengthens the log evidence but is not
        required. A lone filled honeypot on a slow submit is logged as a
        warning and delivered (possible autofill false positive), and a
        missing/garbage/negative ``_ts`` fails open as before.
        """
        request = self.context['request']
        data = request.data
        # Client context for log lines so false positives stay diagnosable.
        client_ip = request.META.get('REMOTE_ADDR', '-')
        user_agent = request.META.get('HTTP_USER_AGENT', '-')

        # Honeypot signal: first candidate field present and non-empty.
        tripped_field = next(
            (field for field in HONEYPOT_FIELDS if data.get(field)), None)

        # Timing signal: submit faster than a human could manage. Fail open on
        # missing/garbage/negative _ts (client clock skew) as unjudgeable.
        fast_submit = False
        elapsed_ms = None
        ts = data.get('_ts')
        if ts is not None:
            try:
                # _ts is epoch milliseconds stamped on the client at form mount.
                elapsed_ms = int(time.time() * 1000) - int(ts)
            except (ValueError, TypeError):
                # Malformed timestamp: cannot judge, so fail open.
                pass
            else:
                fast_submit = 0 <= elapsed_ms < MIN_FORM_SECONDS * 1000

        if fast_submit:
            self.bot_detected = True
            logger.info(
                "Contact form bot detected (elapsed_ms=%s, honeypot_field=%s, "
                "ip=%s, ua=%s).",
                elapsed_ms, tripped_field, client_ip, user_agent)
            return attrs

        if tripped_field:
            # Honeypot filled but the submit took a human amount of time:
            # likely browser autofill, not a bot. Log for visibility and let
            # the message through (truncate the value in case it holds PII).
            logger.warning(
                "Contact form honeypot filled without fast submit; delivering "
                "anyway (field=%s, value=%.50r, ip=%s, ua=%s).",
                tripped_field, data.get(tripped_field), client_ip, user_agent)

        self.bot_detected = False
        return attrs
