from roomballot.models import RoomPlan, Room
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
import os


class Command(BaseCommand):
    help = "Imports per-room floorplans in a directory given as argument."

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str)

    def handle(self, *args, **options):
        print(options['path'][0])
        entries = os.scandir(options['path'][0])
        for entry in entries:
            file = File(open(options['path'][0] + '/' + entry.name))
            rooms = Room.objects.filter(identifier=entry.split(".")[0])
            for room in rooms:
                plan = RoomPlan()
                plan.room = room
                plan.file = file
                plan.save()
