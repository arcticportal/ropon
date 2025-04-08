import logging
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    """
    Wrapper command to call all other commands from the ropon_auth app.
    
    This command will sequentially execute all registered commands in the
    ropon_auth app, logging the results of each execution.
    """
    help = 'Wrapper command to call other commands from the ropon_auth app'

    def handle(self, *args, **options):
        # Set up logger for this command
        logger = logging.getLogger(__name__)
        
        # List of all commands in the ropon_auth app to be run sequentially
        commands_to_run = [
            'assign_user_permissions',
            # Add any future commands here
        ]

        # Execute each command, logging success or failure
        for command in commands_to_run:
            try:
                # Log the start of command execution
                logger.info(f'Running command: {command}\n')
                
                # Call the command
                call_command(command)
                
                # Log successful execution
                logger.info(f'Successfully ran command: {command}\n')
                
            except CommandError as e:
                # Log any errors that occur during command execution
                logger.error(f'Error running command {command}: {e}')
                self.stderr.write(self.style.ERROR(f'Error running command {command}: {e}'))