from roomballot.methods import generate_times, BallotInProgressException
from roomballot.models import Student
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Clears the fields containing picking times.'

    def handle(self, *args, **options):
        try:
            for s in Student.objects.all():
                s.picks_at = None
                s.save()
            self.stdout.write(self.style.SUCCESS('Successfully cleared times.'))
        except BallotInProgressException:
            raise CommandError("The ballot is currently in progress, so you can't do that.")