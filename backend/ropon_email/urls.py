"""
URL Configuration for the ropon_email app.
"""
from django.urls import path
from .views import SendContactEmailAPIView

# Define app_name for namespacing if needed, though not strictly required for include namespace
app_name = 'ropon_email'

urlpatterns = [
    # Map the URL 'contact-us/' to the SendContactEmailAPIView
    path('contact-us/', SendContactEmailAPIView.as_view(), name='send_contact_email'),
]
