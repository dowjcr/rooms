from roomballot.methods import populate_student, BallotInProgressException, StudentAlreadyExistsException, InvalidIdentifierException
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Uses the UIS's Ibis API to get the students from the CRSids in file " \
           "given as argument, and adds them as a first year. Argument: path to list of CRSids, line-separated."

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str)

    def handle(self, *args, **options):
        try:
            for path in options['path']:
                file = open(path, 'r')
                for line in file:
                    populate_student(line.rstrip("\n\r"))
                self.stdout.write(self.style.SUCCESS('Successfully populated database.'))
        except BallotInProgressException:
            raise CommandError("The ballot is currently in progress, so you can't do that.")
        except StudentAlreadyExistsException:
            raise CommandError("Student already exists in the database.")
        except InvalidIdentifierException:
            raise CommandError("A student with that CRSid doesn't exist.")