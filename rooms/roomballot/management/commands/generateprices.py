from roomballot.methods import generate_price, BallotInProgressException
from roomballot.models import Room
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Clears the fields containing picking times.'

    def handle(self, *args, **options):
        try:
            generate_price()
        except BallotInProgressException:
            raise CommandError("The ballot is currently in progress, so you can't do that.")