from roomballot.methods import generate_times, BallotInProgressException
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Generates times at which students will pick their room.'

    def handle(self, *args, **options):
        try:
            generate_times()
            self.stdout.write(self.style.SUCCESS('Successfully generated times.'))
        except BallotInProgressException:
            raise CommandError("The ballot is currently in progress, so you can't do that.")