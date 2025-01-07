import logging
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Wrapper command to call other commands from the ropon_data app'

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        commands_to_run = [
            'assign_cv_permissions',
            'create_observingnetwork_index',
            'load_ropon_cvs'
        ]

        for command in commands_to_run:
            try:
                logger.info(f'Running command: {command}\n')
                call_command(command)
                logger.info(f'Successfully ran command: {command}\n')
            except CommandError as e:
                logger.error(f'Error running command {command}: {e}')
                self.stderr.write(self.style.ERROR(f'Error running command {command}: {e}'))