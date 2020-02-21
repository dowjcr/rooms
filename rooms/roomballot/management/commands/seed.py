from roomballot.models import Setting
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

class Command(BaseCommand):
    help = 'Seeds the database on initial install.'

    def handle(self, *args, **options):
        # Populating setting values.
        setting_names_set_zero = ['weight_ground_floor', 'weight_facing_court', 'weight_facing_lensfield',
                         'feature_price', 'weight_flat', 'weight_renovated_facilities', 'weight_renovated_room',
                         'weight_bathroom', 'total', 'weight_size', 'weight_double_bed', 'weight_ensuite', 'base_price']
        setting_names_set_false = ['allow_review', 'show_prices', 'randomised', 'ballot_in_progress']
        setting_names_set_none = ['current_student', 'start_date']
        with transaction.atomic():
            for name in setting_names_set_zero:
                if Setting.objects.filter(key=name).count() == 0:
                    setting = Setting()
                    setting.key = name
                    setting.value = 0
                    setting.save()
            for name in setting_names_set_false:
                if Setting.objects.filter(key=name).count() == 0:
                    setting = Setting()
                    setting.key = name
                    setting.value = 'false'
                    setting.save()
            for name in setting_names_set_none:
                if Setting.objects.filter(key=name).count() == 0:
                    setting = Setting()
                    setting.key = name
                    setting.save()
        self.stdout.write(self.style.SUCCESS('Successfully seeded database.'))
