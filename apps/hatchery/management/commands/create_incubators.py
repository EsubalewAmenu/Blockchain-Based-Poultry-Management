from django.core.management.base import BaseCommand
from apps.inventory.models import Item
from apps.hatchery.models import Incubators, Hatchery
import random
import string

class Command(BaseCommand):
    help = "Create test data for Incubators model"

    def handle(self, *args, **kwargs):
        self.create_incubators()

    def create_incubators(self):
        hatchery = Hatchery.objects.first()
        if not hatchery:
            self.stdout.write(self.style.ERROR("No hatchery found. Seed hatcheries first."))
            return

        item = Item.objects.filter(item_type__type_name='Incubator').first()
        if not item:
            self.stdout.write(self.style.ERROR("No item found. Seed items first."))
            return

        incubator_data = [
            {
                'incubatortype': 'Single Stage',
                'manufacturer': 'PoultryTech',
                'model': 'PT-100',
                'year': '2022',
            },
            {
                'incubatortype': 'Multi Stage',
                'manufacturer': 'EggMax',
                'model': 'EM-500',
                'year': '2020',
            },
        ]

        for data in incubator_data:
            incubator = Incubators(
                hatchery=hatchery,
                item=item,
                incubatortype=data['incubatortype'],
                manufacturer=data['manufacturer'],
                model=data['model'],
                year=data['year'],
            )
            
            incubator.save()
        

            self.stdout.write(self.style.SUCCESS(f"Created incubator: {incubator.code}"))
        item.quantity = 2
        item.save()