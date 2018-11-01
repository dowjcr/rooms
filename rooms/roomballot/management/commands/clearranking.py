from roomballot.methods import generate_times, BallotInProgressException
from roomballot.models import Student
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Clears the fields containing picking times & rank.'

    def handle(self, *args, **options):
        try:
            for s in Student.objects.filter(year=1):
                s.picks_at = None
                s.rank = None
                s.save()
            self.stdout.write(self.style.SUCCESS('Successfully cleared first-year times and rankings.'))
        except BallotInProgressException:
            raise CommandError("The ballot is currently in progress, so you can't do that.")