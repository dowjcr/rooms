from roomballot.models import RoomPlan, Room
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
import os


class Command(BaseCommand):
    help = "Imports per-room floorplans in a directory given as argument."

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str)

    def handle(self, *args, **options):
        entries = os.scandir(options['path'])
        for entry in entries:
            file = File(open(options['path'] + '/' + entry.name))
            rooms = Room.objects.filter(identifier=entry.split(".")[0])
            for room in rooms:
                plan = RoomPlan()
                plan.room = room
                plan.file = file
                plan.save()
