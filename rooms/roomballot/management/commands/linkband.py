from roomballot.methods import link_band
from roomballot.models import Room
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Converts first-years into second-years, and reverses order accordingly.'

    def handle(self, *args, **options):
        for r in Room.objects.all():
            link_band(r)