from roomballot.email import remind_review
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Sends an email to students who haven't yet reviewed their room."

    def handle(self, *args, **options):
        remind_review()