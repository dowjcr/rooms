from roomballot.methods import update_current_student, ConcurrencyException
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Updates the student who should be picking at this moment.'

    def handle(self, *args, **options):
        try:
            update_current_student()
            self.stdout.write(self.style.SUCCESS('Successfully updated student.'))
        except ConcurrencyException:
            raise CommandError("The ballot hasn't been marked as 'in progress'\nCorrect and try again.")