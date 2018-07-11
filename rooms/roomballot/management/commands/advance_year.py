from roomballot.methods import advance_year, BallotInProgressException
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Converts first-years into second-years, and reverses order accordingly.'

    def handle(self, *args, **options):
        try:
            advance_year()
            self.stdout.write(self.style.SUCCESS('Successfully advanced year.'))
        except BallotInProgressException:
            raise CommandError("The ballot is currently in progress, so you can't do that.")