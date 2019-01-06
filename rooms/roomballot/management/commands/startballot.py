from django.core.management.base import BaseCommand, CommandError
from roomballot.models import Setting, Student
from roomballot.methods import get_setting, set_setting


class NotReadyToStartBallotException(Exception):
    pass


class Command(BaseCommand):
    help = 'Sets ballot as in progress.'

    def handle(self, *args, **options):
        try:
            # Check randomised.
            if get_setting('randomised') != 'true':
                raise NotReadyToStartBallotException()
            # Check all students are complete.
            for student in Student.objects.filter(in_ballot=True):
                if not student.accepted_syndicate or not student.syndicate.complete:
                    raise NotReadyToStartBallotException()
            # Now update setting.
            set_setting('ballot_in_progress', 'true')
            self.stdout.write(self.style.SUCCESS('Successfully started ballot.'))
        except NotReadyToStartBallotException:
            raise CommandError("Not ready to start ballot - perhaps a syndicate is incomplete?")