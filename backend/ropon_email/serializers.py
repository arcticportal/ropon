"""
Serializers for the ropon_email app.
"""
from rest_framework import serializers

class ContactFormSerializer(serializers.Serializer):
    """
    Serializer for validating the contact form data.
    """
    name = serializers.CharField(max_length=100, required=True)
    from_email_id = serializers.EmailField(required=True)
    message = serializers.CharField(required=True)

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
