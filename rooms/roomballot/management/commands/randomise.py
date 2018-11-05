from roomballot.methods import randomise_order, NotReadyToRandomiseException, BallotInProgressException
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

class Command(BaseCommand):
    help = 'Randomises first-year order, and generates times.'

    def handle(self, *args, **options):
        try:
            randomise_order()
            self.stdout.write(self.style.SUCCESS('Successfully randomised order.'))
        except NotReadyToRandomiseException:
            raise CommandError("Not ready to perform randomisation - perhaps a syndicate is incomplete?")
        except BallotInProgressException:
            raise CommandError("Can't perform randomisation because the ballot is in progress.")