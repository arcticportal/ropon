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
# otherwise a bot could learn the full candidate set at once. Simple and effective.
HONEYPOT_FIELDS = ['website', 'url', 'homepage', 'company', 'phone_alt', 'fax']

# Minimum time (seconds) a human is expected to spend on the form. Submissions
# faster than this are treated as a bot. Soft signal: fail-open on
# missing/garbage/negative timestamps so real users aren't blocked.
MIN_FORM_SECONDS = 3


class ContactFormSerializer(serializers.Serializer):
    """
    Serializer for validating the contact form data.

    Detection of likely-bot submissions (honeypot field filled, or submitted
    too fast) happens in ``validate()`` by inspecting the raw request payload
    via ``self.context['request'].data``. DRF drops unknown fields before
    ``validate()`` runs, so the honeypot/``_ts`` fields must be read from the
    raw payload, not from ``attrs``. When a bot is detected the flag
    ``bot_detected`` is set instead of raising: the view then returns a silent
    HTTP 200 so the bot can't tell it was caught.
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

        Honeypot is a hard signal (fail closed when a candidate is filled);
        timing is a soft signal (fail open on missing/garbage/negative ``_ts``).
        """
        data = self.context['request'].data

        # Honeypot: any candidate field present and non-empty => bot.
        for field in HONEYPOT_FIELDS:
            if data.get(field):
                self.bot_detected = True
                logger.info("Contact form honeypot tripped (field=%s).", field)
                return attrs

        # Timing: reject submits faster than a human could manage.
        ts = data.get('_ts')
        if ts is not None:
            try:
                # _ts is epoch milliseconds stamped on the client at form mount.
                elapsed_ms = int(time.time() * 1000) - int(ts)
            except (ValueError, TypeError):
                # Malformed timestamp: cannot judge, so fail open.
                pass
            else:
                # Negative elapsed implies client clock skew; treat as
                # unjudgeable (skip) rather than blocking a real user.
                if 0 <= elapsed_ms < MIN_FORM_SECONDS * 1000:
                    self.bot_detected = True
                    logger.info(
                        "Contact form timing check tripped (elapsed_ms=%s).",
                        elapsed_ms,
                    )
                    return attrs

        self.bot_detected = False
        return attrs
