
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


PASSWORD = "changeme123"

class Command(BaseCommand):
    help = 'Create test users for RoPON'

    def handle(self, *args, **kwargs):
        # get Moderators group if it doesn't exist
        moderators_group = Group.objects.get(name='Moderators')
        
        # Get Editors group if it doesn't exist
        editors_group = Group.objects.get(name='Editors')
        
        # Create roponadmin user
        roponadmin_user, created = User.objects.get_or_create(
            username='roponadmin',
            defaults={
                'first_name': 'ropon',
                'last_name': 'admin',
                'email': 'roponadmin@example.com'
            }
        )
        if created:
            roponadmin_user.set_password(PASSWORD)
            roponadmin_user.save()
            roponadmin_user.groups.add(moderators_group)
            self.stdout.write(self.style.SUCCESS('Created user roponadmin'))

        # Create networkrep user
        networkrep_user, created = User.objects.get_or_create(
            username='networkrep',
            defaults={
                'first_name': 'network',
                'last_name': 'representative',
                'email': 'networkrep@example.com'
            }
        )
        if created:
            networkrep_user.set_password(PASSWORD)
            networkrep_user.save()
            networkrep_user.groups.add(editors_group)
            self.stdout.write(self.style.SUCCESS('Created user networkrep'))
