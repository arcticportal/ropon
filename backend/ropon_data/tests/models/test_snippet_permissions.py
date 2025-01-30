from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.core.management import call_command
from django.apps import apps

from ropon_data.models import (
    ControlledVocabularyModel, Organization
)

class SnippetPermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create groups
        cls.moderators = Group.objects.get(name='Moderators')
        cls.editors = Group.objects.get(name='Editors')
        
        # Models to test
        cls.controlled_vocab_models = [
            model for model in apps.get_app_config('ropon_data').get_models()
            if issubclass(model, ControlledVocabularyModel) and model != ControlledVocabularyModel
        ]
        # Setup permissions using management commands
        
        # Assign controlled vocabulary permissions to moderators
        call_command('assign_cv_permissions')
        
        # Assign snippet permissions to moderators and editors
        call_command('assign_snippet_permissions')

    def test_moderator_permissions(self):
        """Test that moderators have all permissions for all models"""
        for model in self.controlled_vocab_models + [Organization]:
            content_type = ContentType.objects.get_for_model(model)
            for permission in Permission.objects.filter(content_type=content_type):
                self.assertTrue(
                    self.moderators.permissions.filter(id=permission.id).exists(),
                    f"Moderators should have {permission.codename} for {model.__name__}"
                )

    def test_editor_organization_permissions(self):
        """Test that editors have all permissions for Organization model"""
        content_type = ContentType.objects.get_for_model(Organization)
        for permission in Permission.objects.filter(content_type=content_type):
            self.assertTrue(
                self.editors.permissions.filter(id=permission.id).exists(),
                f"Editors should have {permission.codename} for Organization"
            )

    def test_editor_controlled_vocabulary_permissions(self):
        """Test that editors have no permissions for ControlledVocabulary models"""
        for model in self.controlled_vocab_models:
            content_type = ContentType.objects.get_for_model(model)
            permissions = Permission.objects.filter(content_type=content_type)
            
            for permission in permissions:
                self.assertFalse(
                    self.editors.permissions.filter(id=permission.id).exists(),
                    f"Editors should not have {permission.codename} for {model.__name__}"
                )
