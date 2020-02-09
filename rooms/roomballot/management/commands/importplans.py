from roomballot.models import RoomPlan, Room
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Imports per-room floorplans in a directory given as argument."

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str)

    def handle(self, *args, **options):
        
        pass