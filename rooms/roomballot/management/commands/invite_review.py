from roomballot.email import invite_review
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Sends an email to all students, inviting them to review their room.'

    def handle(self, *args, **options):
        invite_review()