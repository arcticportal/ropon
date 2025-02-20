from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from ropon_data.models import Domain, Discipline, MetadataStandard

# Python
# tests/models/test_cv_api.py


class TestControlledVocabularyAPIViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.dom1 = Domain.objects.create(name="Test Domain 1")
        self.dom2 = Domain.objects.create(name="Test Domain 2")
        self.disc1 = Discipline.objects.create(name="Test Discipline 1")
        self.meta1 = MetadataStandard.objects.create(name="Test Metadata Standard 1",
                                                     description="Test Description 1",
                                                     source_url="https://example.com/1")
    def test_list_combined_all(self):
        """GET /cv/ should return combined data for all submodels."""
          # matches /cv/ in get_urlpatterns
        response = self.client.get("/api/v2/cv/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("domains", response.data)
        self.assertIn("disciplines", response.data)
        self.assertIn("metadatastandards", response.data)

    def test_list_domains(self):
        """GET /cv/domains/ should list Domain objects."""
        url = reverse("wagtailapi:cv:listing", args=["domains"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["items"]), 2)
        self.assertEqual(response.data["items"][0]["name"], "Test Domain 1")

    def test_detail_domain_valid(self):
        """GET /cv/domains/<pk>/ should return detail of a specific Domain."""
        url = reverse("wagtailapi:cv:detail", args=["domains", self.dom1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Domain 1")

    def test_detail_domain_invalid_pk(self):
        """GET /cv/domains/999/ should return 404 for nonexistent object."""
        url = reverse("wagtailapi:cv:detail", args=["domains", 999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    
    def test_detail_discipline_valid(self):
        """GET /cv/disciplines/<pk>/ should return detail of a Discipline."""
        url = reverse("wagtailapi:cv:detail", args=["disciplines", self.disc1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Discipline 1")

    def test_detail_metadata_standard_valid_pk(self):
        """GET /cv/metadata_standards/<pk>/ should return detail of a MetadataStandard."""
        url = reverse("wagtailapi:cv:detail", args=["metadatastandards", self.meta1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Metadata Standard 1")
        self.assertEqual(response.data["description"], "Test Description 1")
        self.assertEqual(response.data["source_url"], "https://example.com/1")

    def test_detail_metadata_standard_invalid_pk(self):
        """GET /cv/metadata_standards/999/ should return 404 for nonexistent object."""
        url = reverse("wagtailapi:cv:detail", args=["metadatastandards", 999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_list_metadata_standards(self):
        """GET /cv/metadata_standards/ should list MetadataStandard objects."""
        url = reverse("wagtailapi:cv:listing", args=["metadatastandards"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["name"], "Test Metadata Standard 1")
        self.assertNotIn("description",response.data["items"][0])
        self.assertNotIn("source_url",response.data["items"][0])