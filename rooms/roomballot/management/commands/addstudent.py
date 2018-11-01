from roomballot.methods import populate_student, BallotInProgressException, StudentAlreadyExistsException
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Uses the UIS's Ibis API to get all students not already in the database, and adds them as first years."

    def add_arguments(self, parser):
        parser.add_argument('crsid', nargs='+', type=str)

    def handle(self, *args, **options):
        try:
            for crsid in options['crsid']:
                populate_student(crsid)
                self.stdout.write(self.style.SUCCESS('Successfully populated database.'))
        except BallotInProgressException:
            raise CommandError("The ballot is currently in progress, so you can't do that.")
        except StudentAlreadyExistsException:
            raise CommandError("Student already exists in the database.")