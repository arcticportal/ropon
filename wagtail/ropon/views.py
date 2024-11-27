'''from rest_framework.views import APIView
from rest_framework.response import Response
from cookie_consent.models import CookieConsent


class CookieConsentStatus(APIView):
    def get(self, request):
        consent_status = CookieConsent.objects.filter(
            user=request.user).values('cookie', 'consent')
        return Response(consent_status)
'''
