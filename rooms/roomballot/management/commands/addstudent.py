from roomballot.methods import populate_student, BallotInProgressException, StudentAlreadyExistsException, InvalidIdentifierException
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Uses the UIS's Ibis API to get the student from the CRSid given as argument, and adds them as a first year."

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
        except InvalidIdentifierException:
            raise CommandError("A student with that CRSid doesn't exist.")