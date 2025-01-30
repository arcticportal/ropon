from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from ropon_data.models import Organization

class Command(BaseCommand):
    help = 'Assigns all permissions for Snippet models to Moderators and Editors groups'

    def handle(self, *args, **kwargs):
        try:
            # Get or create the groups
            moderators, _ = Group.objects.get_or_create(name='Moderators')
            editors, _ = Group.objects.get_or_create(name='Editors')

            # Get content type for the model
            content_type = ContentType.objects.get_for_model(Organization)

            # Get all permissions for the model
            permissions = Permission.objects.filter(content_type=content_type)

            # Check if groups already have permissions
            moderator_perms = moderators.permissions.filter(content_type=content_type)
            editor_perms = editors.permissions.filter(content_type=content_type)

            if moderator_perms.exists() and editor_perms.exists():
                self.stdout.write(
                    self.style.WARNING(
                        'Permissions already exist for both groups. No changes made.'
                    )
                )
                return

            # Assign permissions to both groups
            try:
                moderators.permissions.add(*permissions)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to assign permissions to Moderators: {str(e)}')
                )
                return

            try:
                editors.permissions.add(*permissions)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to assign permissions to Editors: {str(e)}')
                )
                return

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully assigned {permissions.count()} permissions to both Moderators and Editors groups'
                )
            )

        except (Group.DoesNotExist, ContentType.DoesNotExist) as e:
            self.stdout.write(
            self.style.ERROR(f'Model or Group not found: {str(e)}')
            )
        except Permission.DoesNotExist as e:
            self.stdout.write(
            self.style.ERROR(f'Permission not found: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
            self.style.ERROR(f'Unexpected error occurred: {str(e)}')
            )